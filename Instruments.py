import web
import config
import itertools
from ImageUploader import upload
from ImageUploader import get_filename
from AppSession import AppSession

render = web.template.render('templates/instruments',
                             base='../base',
                             cache=config.cache)

urls = (
  "", "InstrumentFind",
  "/post", "InstrumentPost",
  "/post/(.+)", "InstrumentPost"
)

labels = {'Excellent' : 'label-success', 'Very Good' : 'label-primary', 'Good' : 'label-info', 'Fair' : 'label-warning', 'Poor' : 'label-danger'}
app = web.application(urls, globals())

from db import Util
util = Util()
appSession = AppSession()

class InstrumentFind:
    def GET(self):
        query = """select *,i.id as instrumentid, to_char(i.created, 'YYYY-MM-DD') as upload_time from instruments i, users u where i.userid=u.id order by i.created desc limit 200"""
        instrument_result = util.db.query(query)
        instruments = list(instrument_result)
        for instrument in instruments:
            instrument['labelCondition'] = labels[instrument.condition]
    	return render.find(instruments)

    def POST(self):
    	i = web.input()
        pagenum=0
        offset=pagenum*10
        term = "%" + i.title + "%"
        if i.location and len(i.location.split(",")) == 2:
            city, state = [l.strip() for l in i.location.split(",")]
            print("Location>> [{}] [{}]".format(city, state))
            query = """select *, i.id as instrumentid, to_char(i.created, 'YYYY-MM-DD') as upload_time  from instruments i, users u where i.userid=u.id and (i.title ilike $term or i.instrument ilike $term) and u.city ilike $city and u.state ilike $state order by i.created desc limit 200"""
            params = dict(term=term, city=city, state=state)
        else:
            query = """select *, i.id as instrumentid, to_char(i.created, 'YYYY-MM-DD') as upload_time  from instruments i, users u where i.userid=u.id and (i.title ilike $term or i.instrument ilike $term) order by i.created desc limit 200"""
            params = dict(term=term)
        instrument_result = util.db.query(query, vars=params)
        instruments = list(instrument_result)
        for instrument in instruments:
            instrument['labelCondition'] = labels[instrument.condition]
        return render.list(instruments, pagenum)

class InstrumentPost:
    def GET(self,instrid=None):
        if not instrid:
            return render.post(params={})
        else:
            instr = util.db.select('instruments', where="id = " + instrid)[0]
            return render.post(params={'instrid': instrid, 'instrument': instr.instrument, 'condition': instr.condition, 'title': instr.title, 'price': instr.price})

    def POST(self):
        i = web.input(instr_img={})
        if(i.title == "" or i.condition == "" or i.price == "" or i.instrument == ""):
            appSession.flash("error", "Title, Instrument and Price are mandatory")
            return render.post(i)
        filename = get_filename(i.get('instr_img', None))
        if filename:
            imagename = filename
            if i.instrid:
                postid = i.instrid
                util.db.update('instruments', where='id='+i.instrid, title=i.title, instrument=i.instrument, condition=i.condition,
                               price=i.price, interest='Seller', userid=web.ctx.session.userid, image_name=imagename)
            else:
                postid = util.db.insert('instruments', title=i.title, instrument=i.instrument, condition=i.condition, price=i.price, interest='Seller', userid=web.ctx.session.userid, image_name=imagename)
            upload('Instrument', i.instr_img, postid)
        else:
            if i.instrid:
                util.db.update('instruments', where='id='+i.instrid, title=i.title, instrument=i.instrument, condition=i.condition,
                               price=i.price, interest='Seller', userid=web.ctx.session.userid)
            else:
                util.db.insert('instruments', title=i.title, instrument=i.instrument, condition=i.condition, price=i.price, interest='Seller', userid=web.ctx.session.userid)
        appSession.flash("success", "Posted instrument title:{} successfully".format(i.title))
        raise web.redirect("")


app_instruments = app