import web
import config
import itertools
from AppSession import AppSession

render = web.template.render('templates/instruments',
                             base='../base',
                             cache=config.cache)

urls = (
  "", "InstrumentFind",
  "/post", "InstrumentPost"
)

labels = {'Excellent' : 'label-success', 'Very Good' : 'label-primary', 'Good' : 'label-info', 'Fair' : 'label-warning', 'Poor' : 'label-danger'}
app = web.application(urls, globals())

from db import Util
util = Util()
appSession = AppSession()

class InstrumentFind:
    def GET(self):
        query = """select *,i.id as instrumentid, to_char(i.created, 'YYYY-MM-DD HH:MI:SS AM') as upload_time from instruments i, users u where i.userid=u.id order by i.created desc limit 200"""
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
        if i.location and len(i.location.split()) == 2:
            city = i.location.split(',')[0].strip()
            state = i.location.split(',')[1].strip()
            print("Location>> [{}] [{}]".format(city, state))
            query = """select *, i.id as instrumentid, to_char(i.created, 'YYYY-MM-DD HH:MI:SS AM') as upload_time  from instruments i, users u where i.userid=u.id and (i.title ilike $term or i.instrument ilike $term) and u.city ilike $city and u.state ilike $state order by i.created desc limit 200"""
            params = dict(term=term, city=city, state=state)
        else:
            query = """select *, i.id as instrumentid, to_char(i.created, 'YYYY-MM-DD HH:MI:SS AM') as upload_time  from instruments i, users u where i.userid=u.id and (i.title ilike $term or i.instrument ilike $term) order by i.created desc limit 200"""
            params = dict(term=term)
        instrument_result = util.db.query(query, vars=params)
        instruments = list(instrument_result)
        for instrument in instruments:
            instrument['labelCondition'] = labels[instrument.condition]
        return render.list(instruments, pagenum)

class InstrumentPost:
    def GET(self):
        return render.post()

    def POST(self):
        i = web.input(instr_img={})
        if(i.title == "" or i.condition == "" or i.price == "" or i.instrument == ""):
            appSession.flash("error", "Title, Instrument and Price are mandatory")
            return render.post()
        if 'instr_img' in i:  # to check if the file-object is created
            filepath = i.instr_img.filename.replace('\\', '/')  # replaces the windows-style slashes with linux ones.
            filename = filepath.split('/')[-1]  # splits the and chooses the last part (the filename with extension)
        postid = util.db.insert('instruments', title=i.title, instrument=i.instrument, condition=i.condition, price=i.price, interest='Seller', userid=web.ctx.session.userid, image_name=filename)
        uploadDir = "/home/prakash/uploads/instruments"
        if 'instr_img' in i:  # to check if the file-object is created
            fout = open(uploadDir + '/' + str(postid) + "_" + filename, 'w')  # creates the file where the uploaded file should be stored
            fout.write(i.instr_img.file.read())  # writes the uploaded file to the newly created file.
            fout.close()  # closes the file, upload complete.
        appSession.flash("success", "Posted instrument title:{} successfully".format(i.title))
        raise web.redirect("")


app_instruments = app