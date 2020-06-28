import base64
import socket
import ssl
from configparser import ConfigParser
import sys

class SMTP():
    def __init__(self):
        self.host = 'smtp.mail.ru'
        self.port = 465
        self.recipient = ''
        self.login = ''
        self.password =''
        self.subject = ''
        self.text = ''
        self.attachment = ''
        self.main()


    def request(self, socket, request):
        try:
            socket.send((request + '\n').encode())
            recv_data = socket.recv(65535).decode()
            return recv_data
        except:
            print("Oops! Something went wrong")
            sys.exit(0)


    def message(self):
        return ( f'From: {self.login}\n'
            f'To: {self.recipient}\n'
            f'Subject: {self.subject}\n'
            'MIME-Version: 1.0\n'
            f'Content-Type: multipart/mixed; boundary="{"___"}"\n\n'
            f'--{"___"}\n'
            'Content-Type: text/plain; charset=utf-8\n'
            'Content-Transfer-Encoding: 8bit\n\n'
            f'{self.text}\n'
            f'--{"___"}\n'
            f'{self.attachment}--\n.')


    def message_parser(self):
        parser = ConfigParser(allow_no_value=True)
        with open('msg.txt', 'r') as f:
            parser.read_file(f)
        sender = parser['From']
        self.login = sender['Login']
        self.password = sender['Password']
        self.recipient = parser['To']['Recipient']
        message = parser['Message']
        self.subject = message['Subject']
        self.text = message['Text']
        self.attachment = self.attachment_parser(message['Attachment'])


    def attachment_parser(self, attachment):
        with open(attachment, 'rb') as file:
            return (f'Content-Disposition: attachment; '
                 f'filename="{attachment}"\n'
                 f'Content-Transfer-Encoding: base64\n'
                 f'Content-Type: name="{file}"\n\n') \
                + base64.b64encode(file.read()).decode() + \
                f'\n--{"___"}\n'


    def decode(self, name):
        return base64.b64encode(name.encode()).decode()


    def main(self):
        self.message_parser()
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
            client.connect((self.host, self.port))
            client = ssl.wrap_socket(client)
            client.recv(1024)
            self.request(client, 'ehlo myUserName')
            self.request(client, 'AUTH LOGIN')
            self.request(client, self.decode(self.login))
            self.request(client, self.decode(self.password))
            self.request(client, 'MAIL FROM:' + self.login)
            self.request(client, 'RCPT TO:' + self.recipient)
            self.request(client, 'DATA')
            self.request(client, self.message())


if __name__ == '__main__':
    smtp = SMTP()
    print("Message is sent")