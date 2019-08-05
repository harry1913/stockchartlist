'''
Created on 2019. 7. 29.

@author: Harry
'''
import configparser
import os

from redis import Redis
from uuid import uuid4

class redis_session():
    
    config = configparser.ConfigParser()
    config.read(os.path.dirname(os.path.abspath( __file__ )) + "/conf/Redisinfo.conf")
    config = config['Redis']    
    
    prefix = config['prefix']
    server_ip = config['server_ip']
    port = config['port']
    timeout = config['timeout']
    
    def __init__(self):
        self.db = Redis(self.server_ip, self.port)
        
    def open_session(self, session_key):
        user_name = self.db.get(self.prefix+session_key)
        
        if user_name is not None:
            self.db.expire(self.prefix+session_key, self.timeout)
            
        return user_name
    
    def save_session(self, user_name):
        session_key = str(uuid4())
        self.db.setex(self.prefix+session_key, self.timeout, user_name)
        
        return session_key
