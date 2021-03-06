from collections import defaultdict

import web
import login
import Books
import Games
import Contact
import Instruments
from AppSession import AppSession

import config
import model as m


urls = (
    '/login', login.app_login,
    '/books', Books.app_books,
    '/games', Games.app_games,
    '/instruments', Instruments.app_instruments,
    '/contact', Contact.app_contact,
    '/logout', 'Logout',
    '/terms', 'Terms',
    '/about', 'About',
    '/google956afd22da6840e3.html', 'GoogleIndex',
    r'/', 'Index',
    )

app = web.application(urls, globals())

from db import Util
util = Util()

render = web.template.render('templates/',
                             base='base',
                             cache=config.cache)


#db = web.database(dbn='postgres', host="127.0.0.1", user='jazzykat', pw='jazzykat', db='k12exchange')
if web.config.get('_session') is None:
  session = web.session.Session(app, web.session.DiskStore('sessions'),
                      initializer={'flash': defaultdict(list), 'userid' : 0, 'username' : ''})
  web.config._session = session
else:
  session = web.config._session


def session_hook():
    web.ctx.session = session
    web.template.Template.globals['session'] = session
    web.template.Template.globals['appSession'] = AppSession()
    web.template.Template.globals['web'] = web

class Index:
    def GET(self):
        #flash("success", """Welcome! Application code lives in app.py,
        #models in model.py, tests in test.py, and seed data in seed.py.""")
        return render.index()

class GoogleIndex:
    def GET(self):
        googlerender = web.template.render('templates/', cache=config.cache)
        return googlerender.google956afd22da6840e3()
 
class About:
    def GET(self):
        return render.about()

class Terms:
    def GET(self):
        return render.terms()

class Logout:
    def GET(self):
        session.username = ''
        session.userid = 0
        session.session_id = ''
        return render.index()
# Set a custom internal error message
def internalerror():
    msg = """
    An internal server error occurred. Please try your request again by
    hitting back on your web browser. You can also <a href="/"> go back
     to the main page.</a>
    """
    return web.internalerror(msg)

app.add_processor(web.loadhook(session_hook))
# Setup the application's error handler
app.internalerror = web.debugerror if web.config.debug else internalerror

if config.email_errors.to_address:
    app.internalerror = web.emailerrors(config.email_errors.to_address,
                                        app.internalerror,
                                        config.email_errors.from_address)


# Adds a wsgi callable for uwsgi
application = app.wsgifunc()
if __name__ == "__main__":
    app.run()
