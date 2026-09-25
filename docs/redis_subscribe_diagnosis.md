# data_service_system：Redis 订阅收不到数据 + gevent 报错 定位报告

日期：2026-09-25
涉及文件：`service/DataService.py`、`dataservice_server.py`、`run.py`、`tools/check_redis_sub.py`
上游发布端：`monitor/src/MsgPub.cpp`、`monitor/src/MonitorOperation.cpp`

---

## 一、结论速览

| 现象 | 结论 |
|---|---|
| `[b'subscribe', b'RMPhysicalAccount', 1]` / `[b'subscribe', b'RMPhysicalAccountOverview', 2]` | **不是数据**，是 Redis 对 `SUBSCRIBE` 命令的确认回执。第三个元素是"当前已订阅频道数"，两次 `subscribe()` 分别得到 1 和 2，所以永远成对出现。 |
| 这些回执"出现多次" | 说明 `subscribe_redis()` 被**反复调用**，即订阅连接被反复重建。 |
| 为什么反复重建 | `socket_timeout=5` 小于发布间隔 10s。空闲 5s 就抛 `TimeoutError`，被 `except` 当成"连接断开"处理 → 重连 → 重新 SUBSCRIBE → 产生新的确认回执。 |
| 是否回归 | **是**。init commit 的 `connect_redis()` 没有 `socket_timeout`、也没有 try/except，`parse_response()` 会一直阻塞，订阅一直有效。当前实现是后来加重连逻辑时引入的。 |
| 为什么是"一条都收不到"而不是"偶尔收到" | 订阅端这个 bug 每约 6s 里有约 5s 是挂在 Redis 上的，按 10s 一条本该偶尔收到。所以"一条都没有"更可能同时还有**发布端**问题：`MsgPub.cpp` 的 lambda 按引用捕获了已出栈的 `pubPassword`（UB），AUTH 可能失效，而 `Publish()` 没传错误回调 → `-NOAUTH` 被静默丢弃。详见第七节。 |
| gevent 报错 | 浏览器中断了 Socket.IO 的长轮询 POST，**非致命**，python-engineio 已捕获并返回 200，只是打了 ERROR 级日志。 |

---

## 二、证据链

### 2.1 客户端是 redis-py 2.x（这是关键前提）

你打印出来的 `[b'subscribe', b'RMPhysicalAccount', 1]` 是**原始 RESP 回执**，不是解析后的结构。这直接锁定了客户端版本：

```python
# redis-py 2.10.6  redis/client.py  ——  PubSub.parse_response
def parse_response(self, block=True, timeout=0):
    "Parse the response from a publish/subscribe command"
    connection = self.connection
    if connection is None:
        raise RuntimeError(
            'pubsub connection not set: '
            'did you forget to call subscribe() or psubscribe()?')
    if not block and not connection.can_read(timeout=timeout):
        return None
    return self._execute(connection, connection.read_response)   # <-- 原始 list
```

redis-py **2.x 直接返回原始 list**；**3.x+** 才通过 `handle_message()` 转成
`{'type': 'subscribe', 'channel': b'...', 'data': 1}` 这样的 dict。

这也解释了为什么老代码 `data[2]` 能跑通：对确认回执 `data[2]` 是 `int`（1、2），
对真实消息 `[b'message', b'<channel>', b'{...json...}']` 才是 `bytes`。
所以 `type(data[2]) is not int` 这个过滤**本身是对的**。

> 注意：2.x 没有 `PubSub.get_message()`（3.0 才有），所以任何修复方案不能依赖它。

### 2.2 重复出现的唯一路径

当前代码里，只有一处会重新发 `SUBSCRIBE`：

```python
except Exception as e:
    log_engine.warning(f'redis pubsub connection error, will retry in {retry_delay}s: {e}')
    sleep(retry_delay)
    try:
        self.subscribe_redis()      # <-- 只有这里
    except Exception as reconnect_error:
        ...
    continue
```

所以"看到多组 `[b'subscribe', ch, 1]` + `[b'subscribe', ch, 2]`" ⟺ "`parse_response()` 反复抛异常"。
结合 2.1，抛的就是 **`redis.exceptions.TimeoutError`**。

### 2.3 触发条件：读超时 ≠ 连接断开

- `socket_timeout=5` 是**读超时**，作用在 pubsub 的 socket 上；
- 发布端的节奏是 `monitor/src/MonitorOperation.cpp:171  calcAccountStatsInterval = 10; // s`
  → 每 10s 才 PUBLISH 一次；
- 于是 5s 读不到数据是**完全正常的空闲**，但 `parse_response()` 会抛 `TimeoutError`；
- 更糟的是 redis-py 的 `_execute()` 在 `TimeoutError` 时会 `connection.disconnect()`
  再抛出（`retry_on_timeout` 默认 False），**socket 已经被关掉**，只能重连。

于是形成循环：

```
t=0.0  SUBSCRIBE ch1, ch2        -> 收到 [b'subscribe', ch1, 1]、[b'subscribe', ch2, 2]
t=0.0  parse_response() 阻塞
t=5.0  TimeoutError -> except -> sleep(1) -> subscribe_redis()  (整条连接重建)
t=6.0  SUBSCRIBE ch1, ch2        -> 又收到一组确认回执
... 循环
```

每轮约 6s，其中 1s+ 完全处于"没订阅"状态，而且重建瞬间的 PUBLISH 直接丢失。
这就是"只能看到 subscribe 回执、看不到数据"的直接原因。

### 2.4 为什么之前没人看到异常

`tools/LogEngine.py:19` 的 `add_console_handler()` 是**注释掉的**，
`log_engine.warning(...)` 只写文件：`log/<YYYYMMDD>_log.txt`。
所以重连告警一直躺在日志里，控制台只能看到 `print()` 出来的确认回执。

---

## 三、如何自己确认（三条命令）

1. **看日志里的超时告警**（最直接的证据）：

   ```bash
   tail -f log/$(date +%Y%m%d)_log.txt | grep 'redis pubsub'
   ```
   如果刷屏 `Timeout reading from socket`，且 `subscribe_redis called!` 也在反复出现，
   就是本文档描述的问题。

2. **确认发布端到底有没有在发**（把"订阅端问题"和"发布端问题"分开）：

   ```bash
   redis-cli -h 127.0.0.1 -p 9379 -a '<password>' MONITOR | grep -iE 'publish|auth'
   ```

   > ⚠️ **MONITOR 单独看是不充分的**：Redis 会把**未通过认证**的客户端的命令也记进
   > MONITOR，只是回一个 `-NOAUTH` 错误。cpp_redis 的 `Publish()` 没有给 `client.publish()`
   > 传 reply 回调，**错误回执会被静默丢掉**。所以"MONITOR 里能看到 PUBLISH"并不代表
   > 消息真的发出去了 —— 这正好能解释"publish 看起来正常、但一条都收不到"。
   >
   > 关键看 **AUTH**：
   > - MONITOR 里先出现 `AUTH "<密码>"` 且其后有 PUBLISH → 发布正常，问题在订阅端；
   > - **只有 PUBLISH、没有 AUTH**（或 AUTH 的密码是乱码）→ 每条 PUBLISH 都被
   >   `NOAUTH` 拒绝并丢弃，问题在 monitor 侧，见第七节。

   交叉验证（错误回执计数，Redis 6.2+）：

   ```bash
   redis-cli -h 127.0.0.1 -p 9379 -a '<password>' INFO stats | grep total_error_replies
   ```
   若该计数以 **12/分钟**（2 条 × 每 10s 一次）的速率稳定增长，就是 PUBLISH 在被拒绝。

   另外也确认一下 monitor 日志里 `redis client connected with host:...` 之后紧跟的
   `auth info: ...` 一行是不是 `OK`。

   如果 MONITOR 里**完全没有 PUBLISH**，则是根本没走到发布：注意
   `MonitorOperation.cpp:27` 的条件是 `iter->second.length() > 0`，
   若 `AccountMonitor::GetCurrentStatus()` 拿到的 `physical` / `overview` 是空串，
   **根本不会调用 Publish**，且不会报任何错（`GetCurrentStatus()` 抛异常也只写 stderr）。

3. **用独立探针跑一遍**（不依赖项目代码，读同一份 ini）：

   ```bash
   python3 tools/check_redis_sub.py --seconds 60
   ```
   输出会明确区分 `subscribe` 回执和 `message` 数据，并在结束时给出结论
   （收到 0 条数据 ⇒ 问题在发布端；收到数据 ⇒ 服务端在丢消息）。
   同时会打印 `PUBSUB NUMSUB` / `PUBSUB CHANNELS`，确认订阅是否真的挂在 Redis 上。

---

## 四、已做的修改

### 4.1 `service/DataService.py`

1. **`socket_timeout` 由 `5` 改为 `30`**
   - 必须**大于**发布间隔（10s），否则健康空闲期就会误判；
   - 也不建议用 `None`：半开连接（NAT/防火墙静默丢包）会永久阻塞、永远不重连；
   - `socket_keepalive=True` 保留；
   - 30s ≈ 3× 发布间隔：正常空闲永不触发，真断线 30s 内自愈。

2. **新增 `extract_redis_payload()`**，同时兼容 redis-py 2.x（原始 list）和 3.x+（dict），
   并显式跳过 `subscribe` / `unsubscribe` / `psubscribe` / `punsubscribe` / `pong`。
   替换掉原来的 `if type(data[2]) is not int:`——后者在客户端升级到 3.x 后会
   直接 `KeyError: 2` 把接收线程打死。

3. **解析与分发拆开**：JSON 解析失败只记一条 warning 并 `continue`，
   不再影响后续消息；`type` 既不是 4 也不是 1 时打一条 warning，便于发现协议变化。

4. **顺带修掉一个潜在崩溃**：老代码的 `if type(data[2]) is not int:` 位于 try 之外，
   而 `[b'pong', b'']` 这类回执只有 **2 个元素**，`data[2]` 会抛 `IndexError`，
   **直接打死接收线程**且没有任何日志。新实现按"回执类型"判断并做长度检查，
   不会再因为非预期回执而中断。已验证 11 种输入（2.x list / 3.x dict / 各种畸形值）全部正确。

### 4.2 `run.py`（新增）

补齐 `run.sh` 一直引用却不存在的入口文件，并做两件事：

1. 首行 `gevent.monkey.patch_all()`，**必须早于** Flask / MySQL / redis 的 import；
2. 可选地过滤 engineio 那条 `post request handler error` 噪音日志
   （`--keep-abort-logs` 可关闭）。

详见第六节。启动方式：

```bash
python3 run.py          # 或 ./run.sh
```

### 4.3 `tools/check_redis_sub.py`（新增）

见第三节第 3 条。

---

## 五、遗留问题（本次未改，建议排期）

1. **`data_queue` 永不清理**：`dataevent/DataQueue.py` 只有两个单槽位，
   `background_thread` 每 10s 把**同一份**数据重复 emit 一次。
   页面会一直显示最后一次快照（能容忍），但"新数据到达"和"重复推送"无法区分。
   另外这两个槽位被订阅线程写、被 SocketIO 线程读，没有加锁（CPython 下勉强安全）。

2. **`run.sh` 与 `run.py`**：`run.sh` 调用的 `run.py` 之前不存在，现已补齐。
   注意 `run.sh` 里是 `2>&1>/dev/null`，stdout/stderr 全部丢弃，
   调试时请直接 `python3 run.py` 或 `python3 dataservice_server.py`。

3. **发布端两个缺陷**：`monitor/src/MsgPub.cpp` 的 lambda 悬空捕获（按引用捕获了
   出栈的局部变量 `pubPassword`）和未初始化的 `isConnected`。
   详见第七节 —— 这两个是"一条数据都收不到"的头号嫌疑。

4. **`run.py` 里没有 `socketio.run()`**：`dataservice_server.py` 的
   `if __name__ == '__main__'` 仍然调用 `socketio.run()`，
   直接跑它仍会出现第六节的报错（无害）。建议统一用 `python3 run.py`。

---

## 六、关于 `post request handler error` / `OSError: unexpected end of file`

### 6.1 不是崩溃

python-engineio 的 `Server.handle_request()` 里，POST 分支是：

```python
try:
    socket.handle_post_request(environ)
    r = self._ok(jsonp_index=jsonp_index)
except exceptions.EngineIOError:
    if sid in self.sockets:
        self.disconnect(sid)
    r = self._bad_request()
except:                                    # <-- 你看到的这条
    self.logger.exception('post request handler error')
    r = self._ok(jsonp_index=jsonp_index)  # 仍然返回 200
```

异常被吞掉，返回 200，服务继续跑。**它既不是数据丢失的原因，也不会让服务挂掉。**

### 6.2 为什么会发生

`gevent/pywsgi.py:234` 在请求体没读全时抛：

```python
if len(read) < length:
    if (use_readline and not read.endswith(b"\n")) or not use_readline:
        raise IOError("unexpected end of file while reading request at position %s" % (self.position,))
```

`position 0` 说明**请求体一个字节都没到**：浏览器发出 `POST`（Socket.IO 长轮询），
然后关掉了连接——关标签页、刷新、跳转、切网络、或者客户端 ping 超时后主动放弃。
engineio 的 `socket.py:112` 正好在 `environ['wsgi.input'].read(length)` 这一步撞上它。

### 6.3 修复方式

**先说一个验证过的死胡同**：不能靠 gevent 的 handler 解决。
gevent 在 `handle_one_response()` 内部就把这个异常捕获了
（它会自己打印 `<request> failed with OSError`），
所以覆盖 `WSGIHandler.handle_one_request()` 或 `handle_error()` **根本收不到它**——
已在本机用「发头不发体再关连接」的方式实测确认：
覆盖 `handle_one_request()` 前后，异常都在到达覆盖点之前就被 gevent 吞掉了。

你看到的 traceback 来自 **engineio 自己的 `logger.exception()`**，
所以只有两个可用的杠杆：

**(a) 减少触发（治本，减少但无法消除）** —— `run.py` 里做了两件事：

1. 第一行就 `gevent.monkey.patch_all()`，且必须在 import Flask / MySQL / redis **之前**。
   这是 gevent 模式的官方要求：不 patch 的话，请求处理里的阻塞调用
   （`/get_*` 那些 MySQL 查询）会卡死整个事件循环，Socket.IO 客户端 ping 超时后
   主动放弃请求 —— 正好制造出这个报错。
2. 建议安装 `gevent-websocket`（`python3 -m pip install gevent-websocket`）。
   没装的话客户端无法升级到 WebSocket，只能一直长轮询，POST 被中断的概率显著变高，
   报错也就更频繁。

**(b) 过滤日志（治标，可选）** —— 在 `engineio.server` 这个 logger 上挂一个
只针对这一条记录的 filter，把它压成一行并放行其他所有 engineio 错误：

```python
class _CondenseAbortedPostLog(logging.Filter):
    def filter(self, record):
        if record.getMessage() != 'post request handler error':
            return True                       # 其他错误原样输出
        exc = record.exc_info[1] if record.exc_info else None
        print('[run.py] dropped an aborted request from the client: %s: %s'
              % (type(exc).__name__, exc))
        return False

logging.getLogger('engineio.server').addFilter(_CondenseAbortedPostLog())
```

为什么挂在 logger 上有效：engineio 的 `Server.__init__` 里是
`self.logger = logging.getLogger('engineio.server')`，
`handle_request()` 直接用这个 logger 打日志，logger 级 filter 一定生效。
（注意 logging 的传播机制：filter 只对**直接经该 logger** 记录的 record 生效，
父 logger 的 filter 不会作用于子 logger 冒泡上来的 record，所以不能挂在 root 上。）
`run.py` 里同时给 root 的 handler 也挂了一份，作为不同 engineio 版本的兜底。

已实测：目标记录被压成一行、其余 engineio 异常仍带完整 traceback 输出。
如果不想要这个过滤，用 `python3 run.py --keep-abort-logs` 即可关闭。

> 结论：**这个报错本身可以不管**（engineio 已吞掉并返回 200）。
> 想让它消失，先装 `gevent-websocket` + 用 `run.py` 启动；还嫌吵再开 filter。

---

## 七、发布端（monitor）的具体缺陷 —— 用来解释"一条都收不到"

订阅端的 bug 能解释**大量丢消息**，但严格来说它每约 6s 里有约 5s 是挂在 Redis 上的，
按 10s 一条的节奏本该偶尔收到。所以"一条都没有"更可能出在发布端。
下面两个是代码里实际存在的缺陷（本次未改，属于 monitor 侧）。

### 7.1 `MsgPub::ConnectRedis()` 的 lambda 捕获了悬空引用（严重）

```cpp
void MsgPub::ConnectRedis() {
    std::string pubAddr = MonitorConfig::GetInstance().GetPubAddr();
    int pubPort = MonitorConfig::GetInstance().GetPubPort();
    std::string pubPassword = MonitorConfig::GetInstance().GetPubPassword();   // 局部变量

    client.disconnect();
    client.connect(pubAddr, pubPort, [&](const std::string &host, size_t port,
                                         cpp_redis::connect_state status) {
        if (status == cpp_redis::connect_state::ok) {
            isConnected = true;
            if (pubPassword.length() > 0) {          // ← 悬空引用！[&] 按引用捕获
                client.auth(pubPassword, [this](const cpp_redis::reply& reply) {
                    LOG_INFO("auth info: {}", reply.as_string());
                });
            }
        }
        ...
    });
    client.sync_commit();
}
```

`client.connect()` 在 cpp_redis 里是**异步**的：它把连接动作 post 到 io_service 线程，
回调是在 `ConnectRedis()` **返回之后**才执行的。而 lambda 用的是 `[&]`，
按引用捕获了 `pubAddr` / `pubPort` / `pubPassword` —— 这三个局部变量此时已经出栈，
`pubPassword.length()` 和 `client.auth(pubPassword, ...)` 读的是已释放的栈内存（UB）。

后果链条：

1. AUTH 可能没发出去，或发出一个乱码密码 → Redis 回 `-NOAUTH`；
2. `Publish()` 里 `client.publish(...)` **没有传 reply 回调**，cpp_redis 不会对错误回执抛异常，
   于是错误被**静默丢弃**，日志里什么都没有；
3. `isConnected` 仍为 `true`（TCP 连上了），所以 `MaintainRedisConnected()` 也不会重连；
4. 表现就是：**发布端"看起来一切正常"，订阅端一条数据都收不到**。

修法：把捕获改成 `[=]` 或 `[this, pubPassword]`（按值捕获），或者把密码存成成员变量。

### 7.2 `isConnected` 从未初始化

```cpp
MsgPub::MsgPub() {
    ConnectRedis();
    maintainFlag = true;
    ...
}
```

`MsgPub.h` 里 `bool isConnected;` 是裸成员，构造函数没有初始化，
而 `ConnectRedis()` 只在**连接成功的回调里**把它置为 `true`。
在回调触发之前它是未定义值，`Publish()` 的 `if (isConnected)` 判断和
`MaintainRedisConnected()` 的 `if (isConnected == false)` 都不可靠。
修法：`MsgPub() : isConnected(false), maintainFlag(false) { ... }`。

### 7.3 顺带排除掉的一个怀疑

曾怀疑 `type` 字段编码不一致（Python 里 `ty == 4` 对字符串 `"4"` 会失败，
而前端 JS 用 `!=` 松散比较不会失败，这种不对称会导致"页面空白但代码看着没错"）。
已核对 `monitor/src/AccountMgr.cpp`：两个 builder 都是
`previewRes.AddMember("type", 4, allocator);` / `detailRes.AddMember("type", 1, allocator);`
—— 是**整数**，`json.loads` 得到 `int`，所以 `ty == 4` / `ty == 1` 匹配正确，**这条排除**。
