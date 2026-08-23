import os
import smtplib
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import threading
from configparser import ConfigParser


class EmailEngine:
    _instance_lock = threading.Lock()

    def __init__(self):
        self.email_from = ''
        self.email_host_password = ''
        self.email_host = ''
        self.email_port = ''
        self.receivers = ''
        program_path = os.path.dirname(os.path.dirname((os.path.abspath(__file__))))
        config_path = os.path.join(program_path, 'config/email.ini')
        self.read_config(config_path)

    def __new__(cls, *args, **kwargs):
        if not hasattr(EmailEngine, "_instance"):
            with EmailEngine._instance_lock:
                if not hasattr(EmailEngine, "_instance"):
                    EmailEngine._instance = object.__new__(cls)
        return EmailEngine._instance

    def read_config(self, config_path):
        if not os.path.exists(config_path):
            print(f'config file: {config_path} does not exist!')
        else:
            config = ConfigParser()
            config.read(config_path)
            self.email_from = config.get('Email', 'email_from')
            self.email_host_password = config.get('Email', 'email_host_password')
            self.email_host = config.get('Email', 'email_host')
            self.email_port = config.get('Email', 'email_port')
            self.receivers = config.get('Email', 'receivers')
            self.set_receivers(self.receivers)

    def set_receivers(self, receivers):
        self.receivers = receivers

    def send_mail(self, subject, content):
        try:
            if not self.receivers:
                return False

            to_emails = self.receivers.replace(' ', '').split(',')  # 收件人邮箱
            if len(to_emails) <= 0:
                print('receive email address is null')
                return False

            msg = MIMEMultipart('alternative')  # 邮件内容
            msg['Subject'] = subject  # 邮件的主题
            msg['From'] = '%s <%s>' % ("通知", self.email_from)
            msg['To'] = '%s <%s>' % ("client", ','.join(to_emails))
            text_plain = MIMEText('{}'.format(content), _subtype='plain', _charset='UTF-8')
            msg.attach(text_plain)

            client = smtplib.SMTP()  # server = smtplib.SMTP_SSL(self.email_host, self.email_port)  # 使用SSL
            client.connect(self.email_host, self.email_port)
            client.login(self.email_from, self.email_host_password)
            client.sendmail(self.email_from, to_emails, msg.as_string())
            client.quit()
            return True
        except Exception as e:
            error_msg = '邮件发送异常, {}'.format(str(e))
            print(error_msg)
        return False

    def send_mail_with_file(self, subject, content, file_path):
        try:
            if not self.receivers:
                return False

            to_emails = self.receivers.replace(' ', '').split(',')  # 收件人邮箱
            if len(to_emails) <= 0:
                print('receive email address is null')
                return False

            msg = MIMEMultipart('alternative')  # 邮件内容
            msg['Subject'] = subject  # 邮件的主题
            msg['From'] = '%s <%s>' % ("Notification", self.email_from)
            msg['To'] = '%s <%s>' % ("client", ','.join(to_emails))
            text_part = MIMEText('{}'.format(content), _subtype='plain', _charset='UTF-8')
            msg.attach(text_part)

            file_part = MIMEApplication(open(file_path, 'rb').read())
            file_part.add_header('Content-Disposition', 'attachment', filename=os.path.basename(file_path))
            msg.attach(file_part)

            client = smtplib.SMTP()  # server = smtplib.SMTP_SSL(self.email_host, self.email_port)  # 使用SSL
            client.connect(self.email_host, self.email_port)
            client.login(self.email_from, self.email_host_password)
            client.sendmail(self.email_from, to_emails, msg.as_string())
            client.quit()
            return True
        except Exception as e:
            error_msg = '邮件发送异常, {}'.format(str(e))
            print(error_msg)
        return False


if __name__ == '__main__':
    email_engine = EmailEngine()
    email_engine.send_mail('Test', 'This is a test!')
