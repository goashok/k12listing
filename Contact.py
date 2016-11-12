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
    	params = dict(seller=i.userid)
    	users = util.db.select('users', params, where='id = $seller')
    	if not users:
            appSession.flash("error", "User {} Not found".format(i.username))
            return web.redirect(referer)
        seller = users[0]
        buyer = web.ctx.session
        seller_subject = "Intersted buyer for your listing on K12Listing.com for {} - {}".format(i.itemtype, i.itemtitle)
        seller_comment =  """
        User {} is trying to contact you for your listing '{}'. Please reply to user  {} directly. Please do not reply to k12listing@gmail.com.
        Comment from buyer:
        {}
        """.format(buyer.username, i.itemtitle, buyer.useremail, i.comment)
        buyer_subject = "Your interest in K12Listing for {} - {}".format(i.itemtype, i.itemtitle)
        buyer_comment = """
        We have sent email to the seller about your interest. You can contact the seller directly at {}.
        Hope your kids enjoy the {}""".format(seller.email, i.itemtype)
        mail.send(seller.email, seller_subject, seller_comment)
        mail.send(buyer.useremail, buyer_subject, buyer_comment)
        appSession.flash("success", "Sent email to the seller. We also sent you the seller's contact")
        raise web.redirect(referer)



app_contact = app
