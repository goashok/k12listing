from collections import defaultdict
import web
import config
from db import Util
from Mail import Sender
from AppSession import AppSession

util = Util()
appSession = AppSession()
mail = Sender()
#import model as m


#VERSION = "0.0.1"

render = web.template.render('templates/login',
                             base='../base',
                             cache=config.cache)

urls = (
  "", "Login",
  "/register", "Register",
  "/settings", "Settings",
  "/forgot", "Forgot"
)

app = web.application(urls, globals())


class Login:
    def GET(self):
    	return render.login()

    def POST(self):
    	i = web.input()
    	params = dict(username=i.username, password=i.password)
    	users = util.db.select('users', params, where='username = $username')
    	if not users:
            appSession.flash("error", "User {} Not found".format(i.username))
            return render.login()
            #return "User {} not found".format(i.username)
        user = users[0]
        if(i.password != user.password):
            appSession.flash("error", "Incorrect password for user {}".format(i.username))
            return render.login()
        web.ctx.session.username = user.username
        web.ctx.session.userid = user.id
        siteurl = web.ctx.env.get('HTTP_HOST', '')
        referer = web.ctx.env.get('DUMMY', "http://"+siteurl)
        raise web.redirect(referer)

class Register:

    def GET(self):
        return render.register()

    def POST(self):
    	i = web.input()
    	params = dict(username=i.username)
    	users = util.db.select('users', params, where="username = $username")
    	if users:
            appSession.flash("error", "Username {} is already registered".format(i.username))
            return render.register()
        else:
            if(i.username == "" or i.first_name == "" or i.last_name == "" or i.age == "" or i.email == ""  or i.password == "" or i.password_confirmation == ""):
                appSession.flash("error", "First/Last Name, Age, Email , Password is required")
                return render.register()
            if int(i.age) < 18:
                appSession.flash("error", "You must be 18 or older to register")
                return render.register()
            if(i.password != i.password_confirmation):
                appSession.flash("error", "Passwords do not match")
                return render.register()
            util.db.insert('users', username=i.username, password=i.password, first_name=i.first_name, last_name=i.last_name, age=i.age, email=i.email, phone=i.phone, city=i.city, state=i.state, zip=i.zip)
            appSession.flash("success", "Successfully registered user {}".format(i.username))
            siteurl = web.ctx.env.get('HTTP_HOST', '')
            referer = web.ctx.env.get('DUMMY', "http://"+siteurl+"/login")
            raise web.redirect(referer)

class Settings:

    def GET(self):
    	username = web.ctx.session.username
    	params = dict(username=username)
    	users = util.db.select('users', params, where='username = $username')
    	if not users:
            appSession.flash("error", "User {} not found".format(i.username))
            return render.settings()
        user = users[0]
        return render.settings(user)

    def POST(self):
    	i = web.input()
    	params = dict(userid=i.userid)
    	userid = i.userid
    	where = ""
    	users = util.db.select('users', params, where="id = $userid")
    	if not users:
            appSession.flash("error", "Cannot find User with id {}".format(i.userid))
            return render.settings(users[0])
    	else:
            if(i.first_name == "" or i.last_name == "" or i.age == "" or i.email == "" or i.phone == ""):
                appSession.flash("error", "First/Last name, age , email, phone is required")
                return render.settings(users[0])
    	    util.db.update('users', where="id = $userid", first_name=i.first_name, last_name=i.last_name, age=i.age, email=i.email, phone=i.phone, vars=params)
            appSession.flash("success", "Updated user {} successfully".format(users[0].username))
    	    return render.settings(users[0])

class Forgot:
    def GET(self):
        return render.forgot()

    def POST(self):
    	i = web.input();
    	params = dict(email=i.email)
    	users = util.db.select('users', params, where="email = $email")
    	if not users:
    		return "Cannot find that email in our system"
    	else:
    		user = users[0]
    		mail.send(i.email, "K12Exchange Password request", "Your password is " + user.password)

app_login = app