function RefreshTable(tableId, json) {
	table = $(tableId).dataTable();
	oSettings = table.fnSettings();
	table.fnClearTable(this); //动态刷新关键部分语句，只会根据后台数据有变化才会刷新
	for (var i = 0; i < json.length; i++)
	{
		table.oApi._fnAddData(oSettings, json[i]); //注意取得的jason串的字符数量，要与html中列的数量要有对应
	}
	oSettings.aiDisplay = oSettings.aiDisplayMaster.slice();
	table.fnDraw();
}

/**
 * Format a number with thousands separators for display.
 * Anything that isn't a finite number is returned unchanged (falls back to
 * '--' for empty/undefined), so it's safe to call on already-formatted
 * strings coming straight from the redis payload.
 */
function formatNumber(value, digits) {
	if (digits === undefined) digits = 2;
	if (value === undefined || value === null || value === '') return '--';
	var num = Number(value);
	if (!isFinite(num)) return value;
	return num.toLocaleString('en-US', {minimumFractionDigits: digits, maximumFractionDigits: digits});
}

/**
 * Toggle a shared "connection status" badge between online/offline
 * (see .conn-status in dashboard.css). containerSelector should point at
 * the element with class conn-status, containing a .conn-label child.
 */
function setConnectionStatus(containerSelector, isOnline) {
	var $container = $(containerSelector);
	$container.toggleClass('is-online', !!isOnline).toggleClass('is-offline', !isOnline);
	$container.find('.conn-label').text(isOnline ? '实时连接中' : '连接已断开，正在重连…');
}

/**
 * Stamp the current time into a connection-status badge's .conn-updated
 * child, to be called whenever a new push is actually received (so users
 * can tell a "connected" socket apart from one that's gone quiet).
 */
function touchLastUpdated(containerSelector) {
	var now = new Date();
	var pad = function (n) { return n < 10 ? '0' + n : n; };
	var text = pad(now.getHours()) + ':' + pad(now.getMinutes()) + ':' + pad(now.getSeconds());
	$(containerSelector).find('.conn-updated').text('更新于 ' + text);
}
