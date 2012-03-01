import sqlite3 as lite
import os

class DB(object):
    def connect(self):
        if not os.path.exists("var/rtfn.db"):
            self.create()
        self.__link = lite.connect("var/rtfn.db")
        self.__cur = self.__link.cursor()
        pass 
    
    def create_tables(self):
        link = lite.connect("var/rtfn.db")
        cur = link.cursor()
        cur.execute("create table IF NOT EXISTS competitions( \
            c_id INTEGER Primary Key, \
            name TEXT unique, \
            key TEXT NOT NULL, \
            state DATETIME Default CURRENT_TIMESTAMP, \
            end DATETIME Default CURRENT_TIMESTAMP \
        ) ")
        cur.execute("create table IF NOT EXISTS users( \
            u_id INTEGER PRIMARY KEY, \
            name TEXT unique, \
            register DATETIME Default CURRENT_TIMESTAMP \
        )")
        cur.execute("create table IF NOT EXISTS user_competition( \
            c_id Integer, \
            u_id Integer, \
            FOREIGN KEY(c_id) REFERENCES competitions(c_id), \
            FOREIGN KEY(u_id) REFERENCES users(u_id) \
        )")
        link.close()
        pass
     
    def create_user(self, user, key):
        pass
    
    def create_competition(self, name, key):
        pass
    
    def get_user(self, user, competition):
        pass
    
    def make_admin(self, user):
        pass