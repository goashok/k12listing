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
        query = """select *,b.id as bookid, to_char(b.created, 'YYYY-MM-DD HH:MI:SS AM') as upload_time from books b, users u where b.userid=u.id order by b.created desc limit 200"""
        book_result = util.db.query(query)
        books = list(book_result)
        for book in books:
            book['labelCondition'] = labels[book.condition]
    	return render.find(books)

    def POST(self):
    	i = web.input()
        pagenum=0
        offset=pagenum*10
        if not i.term:
            appSession.flash("error", "No search term specified")
            return render.find(books=[])
        isbnLkup = IsbnLookup()
        try:
            meta = isbnLkup.find(i.term)
        except:
            meta = None
        if meta:
            isbn13 = meta['ISBN-13']
        else:
            isbn13 = ''
        searchTerm = '%' + i.term + "%"
        if i.location and len(i.location.split()) == 2:
            city = i.location.split(',')[0].strip()
            state = i.location.split(',')[1].strip()
            print("Location>> [{}] [{}]".format(city, state))
            query = """select *,b.id as bookid, to_char(b.created, 'YYYY-MM-DD HH:MI:SS AM') as upload_time from books b, users u where b.userid=u.id and (b.isbn = $term or b.isbn13 = $isbn13 or b.title ilike $searchTerm or b.author ilike $searchTerm) and u.city ilike $city and u.state ilike $state order by b.created desc limit 200"""
            params = dict(term=i.term, isbn13=isbn13, city=city, state=state, searchTerm=searchTerm)
        else:
            query = """select *, b.id as bookid, to_char(b.created, 'YYYY-MM-DD HH:MI:SS AM') as upload_time from books b, users u where b.userid=u.id and (b.isbn = $term or b.isbn13 = $term or b.title ilike $searchTerm or b.author ilike $searchTerm) order by b.created desc limit 200"""
            params = dict(term=i.term, isbn13=isbn13, searchTerm=searchTerm)
        book_result = util.db.query(query, vars=params)
        books = list(book_result)
        if meta:
            meta['Authors']=','.join(map(str, meta['Authors']))
        for book in books:
            book['labelCondition'] = labels[book.condition]
        return render.list(books, meta, pagenum)

class BookPost:
    def strip(self, param):
        return param.strip()

    def GET(self):
        return render.post()

    def POST(self):
        i = web.input()
        attrs = ['title', 'author', 'isbn']
        for attr in attrs:
            attrval = str(getattr(i, attr)).strip()
            setattr(i, attr, attrval)
            if attr == "isbn":
                setattr(i, attr, attrval.replace(" ", ""))
        isbnLkup = IsbnLookup()
        if not i.isbn:
            appSession.flash("error", "No isbn specified")
            return render.post()
        try:
            meta = isbnLkup.find(i.isbn)
        except:
            meta = {'ISBN-13' : i.isbn}
        if not meta:
            meta = {'ISBN-13' : i.isbn}
        isbn13 = meta['ISBN-13']
        if(i.isbn == "" or i.condition == "" or i.title == "" or i.price == "" or i.price == "$"):
            appSession.flash("error", "ISBN, Title, Condition and Price are mandatory")
            return render.post()
        util.db.insert('books', isbn=i.isbn, isbn13=isbn13, condition=i.condition, price=i.price.replace("$",""), author=i.author, title=i.title, interest='Seller', userid=web.ctx.session.userid)
        appSession.flash("success", "Posted book isbn:{} successfully".format(i.isbn))
        raise web.redirect("")


app_books = app
