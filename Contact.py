from collections import defaultdict
import web
import config
from db import Util
from Mail import Sender
from AppSession import AppSession

util = Util()
appSession = AppSession()
mail = Sender()

render = web.template.render('templates/contact',
                             base='../base',
                             cache=config.cache)

urls = (
  "", "ContactSeller"
)

app = web.application(urls, globals())

labels = {'Excellent' : 'label-success', 'Very Good' : 'label-primary', 'Good' : 'label-info', 'Fair' : 'label-warning', 'Poor' : 'label-danger'}


class ContactSeller:

    def POST(self):
        referer = web.ctx.env.get('HTTP_REFERER', '')
        if not web.ctx.session.userid:
            appSession.flash("error", "You need to be signed in to contact the seller")
            raise web.redirect(referer)
    	i = web.input()
    	params = dict(postedby=i.userid)
    	users = util.db.select('users', params, where='id = $postedby')
    	if not users:
            appSession.flash("error", "User {} Not found".format(i.username))
            return web.redirect(referer)
        postedby_user = users[0]
        subject = "Intersted buyer for your listing on K12Listing.com for {} - {}".format(i.itemtype, i.itemtitle)
        comment = i.comment + """
        Please reply to user  {} directly. DO NOT reply to k12listing@gmail.com.
        """.format(web.ctx.session.useremail)
        mail.send(postedby_user.email, subject, comment, cc=web.ctx.session.useremail)
        appSession.flash("success", "Sent email to user. You have been cc-ed on the email sent to seller")
        raise web.redirect(referer)



app_contact = app
