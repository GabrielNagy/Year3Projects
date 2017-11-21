#!/usr/bin/env python
import couchdbkit


if __name__ == "__main__":
    couchdbkit.set_logging('info')
    ip = "http://admin:admin@127.0.0.1:5984"
    database = "flaskr"
    server = couchdbkit.Server(ip)
    db = server.get_or_create_db(database)
    couchdbkit.designer.push('_design/users', db)
