import web


web.config.smtp_server = 'smtp.gmail.com'
web.config.smtp_port = 587
web.config.smtp_username = 'goashok@gmail.com'
web.config.smtp_password = ''
web.config.smtp_starttls = True


class Sender:
    def send(self, to, subject, message):
      web.sendmail("goashok@gmail.com", to, subject, message) 
