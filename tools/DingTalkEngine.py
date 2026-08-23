import os
from dingtalkchatbot.chatbot import DingtalkChatbot
import threading
from configparser import ConfigParser


class DingTalkEngine:
    _instance_lock = threading.Lock()

    def __init__(self):
        self.webhook = ''
        self.secret = ''
        program_path = os.path.dirname(os.path.dirname((os.path.abspath(__file__))))
        config_path = os.path.join(program_path, 'config/dingtalk.ini')
        self.read_config(config_path)
        self.ding_talk = DingtalkChatbot(self.webhook, secret=self.secret)

    def __new__(cls, *args, **kwargs):
        if not hasattr(DingTalkEngine, "_instance"):
            with DingTalkEngine._instance_lock:
                if not hasattr(DingTalkEngine, "_instance"):
                    DingTalkEngine._instance = object.__new__(cls)
        return DingTalkEngine._instance

    def read_config(self, config_path):
        if not os.path.exists(config_path):
            print(f'config file: {config_path} does not exist!')
        else:
            config = ConfigParser()
            config.read(config_path)
            self.webhook = config.get('DingTalk', 'webhook')
            self.secret = config.get('DingTalk', 'secret')

    def send_msg(self, msg, is_at_all=False):
        self.ding_talk.send_text(msg=msg, is_at_all=is_at_all)


ding_talk_engine = DingTalkEngine()

if __name__ == '__main__':
    ding_talk_engine.send_msg('This is a test!', True)
