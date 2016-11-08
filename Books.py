import web
import config
import itertools
from isbn_lookup import IsbnLookup
from AppSession import AppSession


render = web.template.render('templates/books',
                             base='../base',
                             cache=config.cache)

urls = (
  "", "BookFind",
  "/post", "BookPost"
)

labels = {'Excellent' : 'label-success', 'Very Good' : 'label-primary', 'Good' : 'label-info', 'Fair' : 'label-warning', 'Poor' : 'label-danger'}
app = web.application(urls, globals())

from db import Util
util = Util()
appSession = AppSession()

class BookFind:
    def GET(self):
    	return render.find()

    def POST(self):
    	i = web.input()
        pagenum=0
        offset=pagenum*10
        if not i.isbn:
            appSession.flash("error", "No isbn specified")
            return render.find()
        isbnLkup = IsbnLookup()
        meta = isbnLkup.find(i.isbn)
        isbn13 = meta['ISBN-13']
    	params = dict(isbn=i.isbn, isbn13=isbn13)
        book_result = util.db.query('select * from books b, users u where b.userid=u.id and (b.isbn = $isbn or b.isbn13 = $isbn13) order by b.created desc', vars={'isbn' : i.isbn, 'isbn13' : isbn13})
        books = list(book_result)
        meta['Authors']=','.join(map(str, meta['Authors']))
        for book in books:
            book['labelCondition'] = labels[book.condition]
        return render.list(books, meta, pagenum)

class BookPost:
    def GET(self):
        return render.post()

    def POST(self):
        i = web.input()
        isbnLkup = IsbnLookup()
        if not i.isbn:
            appSession.flash("error", "No isbn specified")
            return render.post()
        meta = isbnLkup.find(i.isbn)
        isbn13 = meta['ISBN-13']
        if(i.isbn == "" or i.condition == "" or i.price == ""):
            appSession.flash("error", "Condition and Price are mandatory")
            return render.post()
        util.db.insert('books', isbn=i.isbn, isbn13=isbn13, condition=i.condition, price=i.price, author=i.author, title=i.title, interest='Seller', userid=web.ctx.session.userid)
        appSession.flash("success", "Posted book isbn:{} successfully".format(i.isbn))
        raise web.redirect("")


app_books = app