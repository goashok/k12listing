import web
from collections import defaultdict

VERSION = "0.0.1"

class Util:
    db = web.database(dbn='postgres', host="127.0.0.1", user='jazzykat', pw='jazzykat', db='k12exchange')
    session = None
    def __init__(self):
    	pass