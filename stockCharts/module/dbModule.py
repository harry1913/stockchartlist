
import os
import pymysql
import configparser

class Database():
    def __init__(self):
         
        config = configparser.ConfigParser()
        config.read(os.path.dirname(os.path.abspath( __file__ )) + "/conf/DBinfo.conf")
        config = config['DB']
        
        self.db = pymysql.connect(host = config['host'],
                                  port = int(config['port']),
                                  user = config['user'],
                                  password = config['passwd'],
                                  db = config['db'],
                                  charset = config['charset'])
        
        self.cursor = self.db.cursor(pymysql.cursors.DictCursor)
        
    def execute(self, query, args={}):
        self.cursor.execute(query, args)
        
    def executeOne(self, query, args={}):
        self.cursor.execute(query, args)
        row = self.cursor.fetchone()
        return row
        
    def executeAll(self, query, args={}):
        self.cursor.execute(query, args)
        row = self.cursor.fetchall()
        return row
 
    def commit(self):
        self.db.commit()
    
    def rollback(self):
        self.db.rollback()
           
    def close(self):
        self.db.close()
