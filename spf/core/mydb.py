#!/usr/bin/env python

import sqlite3
import sys
from utils import Utils

class MyDB():
    def __init__(self, sqlite_file):
        self.sqlite_file = sqlite_file + "spf.sqlite"
        print self.sqlite_file
        self.conn = None
        if (not self.checkDB()):
            self.initDB()

    def getCursor(self):
        if (self.conn == None):
            print self.sqlite_file
            try:
                self.conn = sqlite3.connect(self.sqlite_file)
            except sqlite3.OperationalError as e:
                print e
            except:
                print sys.exc_info()[0]
        return self.conn.cursor()

    def checkDB(self):
        try:
            cursor = self.getCursor()
        except:
            print sys.exc_info()[0]
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
        if cursor.fetchone() is None:
            return False

        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='hosts'")
        if cursor.fetchone() is None:
            return False

        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='web_templates'")
        if cursor.fetchone() is None:
            return False

        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='ports'")
        if cursor.fetchone() is None:
            return False

        return True

    def initDB(self):
        cursor = self.getCursor()
        cursor.execute("DROP TABLE IF EXISTS users")
        cursor.execute("CREATE TABLE users(user TEXT)")

        cursor.execute("DROP TABLE IF EXISTS hosts")
        cursor.execute("CREATE TABLE hosts(name TEXT, ip TEXT)")

        cursor.execute("DROP TABLE IF EXISTS web_templates")
        cursor.execute("CREATE TABLE web_templates(ttype TEXT, src_url TEXT, tdir TEXT)")

        cursor.execute("DROP TABLE IF EXISTS ports")
        cursor.execute("CREATE TABLE ports(port INTEGER, host TEXT)")
        self.conn.commit()
        return

    def addUser(self, user):
        cursor = self.getCursor()
        cursor.execute('INSERT INTO users VALUES(?)', (user,))
        self.conn.commit()
        return

    def addUsers(self, users):
        for user in users:
            self.addUser(user)
        return

    def addHost(self, name, ip=""):
        cursor = self.getCursor()
        cursor.execute('INSERT INTO hosts VALUES(?,?)', (name, ip,))
        self.conn.commit()
        return

    def addHosts(self, hosts):
        for host in hosts:
            self.addHost(host)
        return

    def addPort(self, port, host):
        cursor = self.getCursor()
        cursor.execute('INSERT INTO ports VALUES(?,?)', (port, host,))
        self.conn.commit()
        return

    def addWebTemplate(self, ttype, src_url, tdir):
        cursor = self.getCursor()
        cursor.execute('INSERT INTO web_templates VALUES(?,?,?)', (ttype, src_url, tdir,))
        self.conn.commit()
        return

    def getUsers(self):
        users = []
        cursor = self.getCursor()
        cursor.execute('SELECT user FROM users')
        for row in cursor.fetchall():
            users.append(row[0])
        return Utils.unique_list(users)
        
    def getWebTemplates(self, ttype="static"):
        templates = []
        cursor = self.getCursor()
        cursor.execute('SELECT src_url, tdir FROM web_templates WHERE ttype=?', (ttype,))
        for row in cursor.fetchall():
            templates.append(row[1]+"[-]"+row[0])
        return Utils.unique_list(templates)
