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
        query = """select *,g.id as gameid, to_char(g.created, 'YYYY-MM-DD HH:MI:SS AM') as upload_time from games g, users u where g.userid=u.id order by g.created desc limit 200"""
        game_result = util.db.query(query)
        games = list(game_result)
        for game in games:
            game['labelCondition'] = labels[game.condition]
    	return render.find(games)

    def POST(self):
    	i = web.input()
        pagenum=0
        offset=pagenum*10
        titleQueryStr = "%" + i.title + "%"
        if i.location and len(i.location.split()) == 2:
            city = i.location.split(',')[0].strip()
            state = i.location.split(',')[1].strip()
            print("Location>> [{}] [{}]".format(city, state))
            query = """select *, g.id as gameid, to_char(g.created, 'YYYY-MM-DD HH:MI:SS AM') as upload_time  from games g, users u where g.userid=u.id and g.title ilike $title and u.city ilike $city and u.state ilike $state order by g.created desc limit 200"""
            params = dict(title=titleQueryStr, city=city, state=state)
        else:
            query = """select *, g.id as gameid, to_char(g.created, 'YYYY-MM-DD HH:MI:SS AM') as upload_time  from games g, users u where g.userid=u.id and g.title ilike $title order by g.created desc limit 200"""
            params = dict(title=titleQueryStr)
        game_result = util.db.query(query, vars=params)
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
            appSession.flash("error", "Title, Condition and Price are mandatory")
            return render.post()
        util.db.insert('games', title=i.title, console=i.console, condition=i.condition, price=i.price, interest='Seller', userid=web.ctx.session.userid)
        appSession.flash("success", "Posted game title:{} successfully".format(i.title))
        raise web.redirect("")


app_games = app