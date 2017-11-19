#!/usr/bin/env python
import datetime
from couchdbkit import *

server = Server()

db = server.get_or_create_db("greeting")

doc = {"mydoc": "test"}
db.save_doc(doc)


class Greeting(Document):
    author = StringProperty()
    content = StringProperty()
    date = DateTimeProperty()


Greeting.set_db(db)

greet = Greeting(author="Gaboaje", content="Continut blana", date=datetime.utcnow())

greet.save()
