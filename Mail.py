import web
import os

lines = tuple(open('./passwd.txt', 'r'))
web.config.smtp_server = 'smtp.gmail.com'
web.config.smtp_port = 587
web.config.smtp_username = 'k12listing@gmail.com'
web.config.smtp_password = lines[0]
print(">>> PASS>> " + web.config.smtp_password)
web.config.smtp_starttls = True


class Sender:
    def send(self, to, subject, message, cc=None):
      web.sendmail("k12listing@gmail.com", to, subject, message, cc=cc) 
