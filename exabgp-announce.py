#!/usr/bin/env python

import time
import datetime
import sys
import json

# Basic SQL Object framework
import peewee
from peewee import *

# Basic web server to answer REST queries
import web

### Initialize Peewee model / db

db = MySQLDatabase('rdb', host='localhost', user='rdb', passwd='rdbcbcc')
class BaseModel(Model):
    class Meta:
        database = db

class Route(BaseModel):
    prefix  = CharField()
    nexthop = CharField()
    added   = DateTimeField(default=datetime.datetime.now)
    updated = DateTimeField(default=datetime.datetime.now)
    def json(self):
        return( '{"id": "' + str(self.id) + '", "prefix": "'+self.prefix+'", "nexthop": "' + self.nexthop
                + '", "added": "' + self.added.strftime("%Y-%m-%d %H:%M:%S")
                + '", "updated": "' + self.updated.strftime("%Y-%m-%d %H:%M:%S") + '"}' )

try:
    db.connect()
except:
    try: db.init('rdb', host='localhost', user='rdb', passwd='rdbcbcc')
    except: pass

try:
    for r in Route.select():
        pass
except:
    try: db.create_tables([Route])
    except: pass


### Initialize REST web server
urls = (
    # GET List routes or POST a new one
    '/routes/', 'routes',
    # GET a specific route ID or pattern or PUT a modification
    '/routes/(.*)', 'route',
)

def addroute(prefix,nexthop):
    sys.stdout.write("announce route " + str(prefix) + " next-hop " + str(nexthop) + "\n")
    sys.stdout.flush()

def delroute(prefix,nexthop):
    sys.stdout.write("withdraw route " + str(prefix) + " next-hop " + str(nexthop) + "\n")
    sys.stdout.flush()

app = web.application(urls, globals())

class routes:
    def GET(self):
        i = web.input(prefix=None,nexthop=None)
        if i.prefix is None:
            if i.nexthop is None:
                rs = Route.select()
            else:
                rs = Route.select(Route.nexthop == i.nexthop)
        elif i.nexthop is None:
            rs = Route.select(Route.prefix == i.prefix)
        else:
            rs = Route.select(Route.prefix == i.prefix, Route.nexthop == i.nexthop)

        output = '{"routes":['
        jr = list()
        for r in rs:
            jr.append(r.json())
        output += ",".join(jr)
        output += ']}';
        return output
    def POST(self):
        i = web.input()
        r = Route.create(prefix=i.prefix, nexthop=i.nexthop)
        r.save()
        addroute(r.prefix, r.nexthop)
        return '/routes/' + str(r.id)


class route:
    def DELETE(self, id):
        try:
            r = Route.get(Route.id == id)
            out = str(r.json())
            delroute(r.prefix,r.nexthop)
            r.delete_instance()
            return out
        except:
            return '{"null"}'

    def GET(self, id):
        try:
            r = Route.get(Route.id == id)
            return str(r.json())
        except:
            return '{"null"}'

    def PUT(self, id):
        i = web.input(prefix=None,nexthop=None)
        try:
            r = Route.get(Route.id == id)

        except:
            return '{"null"}'
            
        oldprefix=r.prefix
        oldnexthop=r.nexthop

        if i.prefix is not None:
            r.prefix = i.prefix
        if i.nexthop is not None:
            r.nexthop = i.nexthop
        r.updated = datetime.datetime.now()
        r.save()

        delroute(oldprefix,oldnexthop)
        addroute(r.prefix, r.nexthop)
        return str(r.json())

if __name__ == "__main__":

    rs = Route.select()
    for r in rs:
        addroute(r.prefix, r.nexthop)

    app.run()
