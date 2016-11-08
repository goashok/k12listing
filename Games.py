import web
import config
import itertools
from AppSession import AppSession

render = web.template.render('templates/games',
                             base='../base',
                             cache=config.cache)

urls = (
  "", "GameFind",
  "/post", "GamePost"
)

labels = {'Excellent' : 'label-success', 'Very Good' : 'label-primary', 'Good' : 'label-info', 'Fair' : 'label-warning', 'Poor' : 'label-danger'}
app = web.application(urls, globals())

from db import Util
util = Util()
appSession = AppSession()

class GameFind:
    def GET(self):
    	return render.find()

    def POST(self):
    	i = web.input()
        pagenum=0
        offset=pagenum*10
        titleQueryStr = "%" + i.title + "%"
        game_result = util.db.query('select * from games g, users u where g.userid=u.id and g.title ilike $title order by g.created desc', vars={'title' : titleQueryStr})
        games = list(game_result)
        for game in games:
            game['labelCondition'] = labels[game.condition]
        return render.list(games, pagenum)

class GamePost:
    def GET(self):
        return render.post()

    def POST(self):
        i = web.input()
        if(i.title == "" or i.condition == "" or i.price == "" or i.console == ""):
            return "Title, Console, Condition & Price fields are mandatory"
        util.db.insert('games', title=i.title, console=i.console, condition=i.condition, price=i.price, interest='Seller', userid=web.ctx.session.userid)
        appSession.flash("success", "Posted game title:{} successfully".format(i.title))
        raise web.redirect("")


app_games = app