#!/usr/bin/env python
import couchdbkit
import os


if __name__ == "__main__":
    couchdbkit.set_logging('info')
    if 'COUCHDB_USER' and 'COUCHDB_PASS' in os.environ:
        ip = "http://%s:%s@127.0.0.1:5984" % (os.getenv('COUCHDB_USER'), os.getenv('COUCHDB_PASS'))
    else:
        ip = "http://admin:admin@127.0.0.1:5984"
    database = "upload_app"
    server = couchdbkit.Server(ip)
    db = server.get_or_create_db(database)
    couchdbkit.designer.push('_design/users', db)
