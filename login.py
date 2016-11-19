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
  "/forgot", "Forgot",
  "/manage", "Manage",
  "/delete/(.+)/(.+)", "Delete"
)

app = web.application(urls, globals())

labels = {'Excellent' : 'label-success', 'Very Good' : 'label-primary', 'Good' : 'label-info', 'Fair' : 'label-warning', 'Poor' : 'label-danger'}


class Login:
    def GET(self):
    	return render.login()

    def POST(self):
    	i = web.input()
        i.username = i.username.lower()
    	params = dict(username=i.username, password=i.password)
    	users = util.db.select('users', params, where='username = $username')
        siteurl = web.ctx.env.get('HTTP_HOST', '')
        referer = web.ctx.env.get('DUMMY', "http://"+siteurl)
    	if not users:
            appSession.flash("error", "User {} Not found".format(i.username))
            return web.redirect(referer)
        user = users[0]
        if(i.password != user.password):
            appSession.flash("error", "Incorrect password for user {}".format(i.username))
            return web.redirect(referer)
        web.ctx.session.username = user.username
        web.ctx.session.userid = user.id
        web.ctx.session.useremail = user.email
        raise web.redirect(referer)

class Register:

    def GET(self):
        return render.register()

    def POST(self):
    	i = web.input()
        i.username = i.username.lower()
        i.email = i.email.lower()
    	params = dict(username=i.username, email=i.email)
        users_byemail = util.db.select('users', params, where="email = $email")
        if users_byemail:
            appSession.flash("error", "User with email {} already exists".format(i.email))
            return render.register()
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
            referer = web.ctx.env.get('DUMMY', "http://"+siteurl)
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
    	    mail.send(i.email, "K12Listing Password request", "Your username/password is " + user.username + "/" + user.password)
            appSession.flash("success", "Information about your login has been mailed")
            return render.forgot()

class Manage:
    def GET(self):
        query = """select u.id as userid, u.username, u.email, b.id as itemid, b.title, b.price, b.condition, b.isbn as identifier, 'Book' as type, to_char(b.created, 'YYYY-MM-DD') as created, b.image_name
                   from users u, books b
                   where u.id=$userid and u.id = b.userid
                   union
                   select u.id as userid, u.username, u.email, g.id as itemid, g.title, g.price, g.condition , g.console as identifier, 'Game' as type, to_char(g.created, 'YYYY-MM-DD') as created, g.image_name
                   from users u, games g
                   where u.id=$userid and u.id = g.userid
                   union
                   select u.id as userid, u.username, u.email, i.id as itemid, i.title, i.price, i.condition , i.instrument as identifier, 'Instrument' as type, to_char(i.created, 'YYYY-MM-DD') as created, i.image_name
                   from users u, instruments i
                   where u.id=$userid and u.id = i.userid
                   """
        items_result = util.db.query(query, vars={'userid' : web.ctx.session.userid})
        items = list(items_result)
        for item in items:
            item['labelCondition'] = labels[item.condition]
        return render.manage(items)

class Delete:
    def GET(self, itemType, itemId):
        print "Deleting " + itemType + "," + itemId
        itemIdInt = int(itemId)
        if itemType == "Book":
            books = util.db.select("books", vars=locals(), where="id = $itemIdInt")
            if books and books[0].userid == web.ctx.session.userid:
                util.db.delete('books', where="id=$itemIdInt", vars=locals())
            else:
                appSession.flash("error", "Cannot find book or you are not the owner of the posting")
                return Manage().GET()
        if itemType == "Game":
            games = util.db.select("games", vars=locals(), where="id = $itemIdInt")
            if games and games[0].userid == web.ctx.session.userid:
                util.db.delete('games', where="id=$itemIdInt", vars=locals())
            else:
                appSession.flash("error", "Cannot find game or you are not the owner of the posting")
                return Manage().GET()
        if itemType == "Instrument":
            instruments = util.db.select("instruments", vars=locals(), where="id = $itemIdInt")
            if instruments and instruments[0].userid == web.ctx.session.userid:
                util.db.delete('instruments', where="id=$itemIdInt", vars=locals())
            else:
                appSession.flash("error", "Cannot find " + itemType + " or you are not the owner of the posting")
                return Manage().GET()

        return Manage().GET()


app_login = app
