'''
Created on 2019. 7. 29.

@author: Harry
'''

from module import dbModule
from werkzeug.security import generate_password_hash, check_password_hash
from pymysql.err import MySQLError

class User(object):
    
    def __init__(self, id, password, username='nothing', userclass='none', userclasscode='02', userphone='none', useremail='none'):
        
        self.user_id = id
        
        self.user_name = username

        self.password = password
        
        self.user_class = userclass
        
        self.user_class_code = userclasscode
        
        self.user_phone = userphone
        
        self.user_email = useremail
                
        self.conn = dbModule.Database()
        
    
    def set_password(self, password=None):
        
        if password is None:
            
            password = self.password
            
        pw_hash = generate_password_hash(password)
        
        return pw_hash
    
    def check_password(self, pw_hash):
        return check_password_hash(pw_hash, self.password)
    
    def create_user(self):
        try:
            sql = "REPLACE INTO User (user_Id, user_Name, user_Password, user_Class, user_ClassCode, user_Phone, user_Email, comm_date) \
                    VALUES ('{0}', '{1}', '{2}', '{3}', '{4}', '{5}', '{6}', now())"
                    
            sql = sql.format(self.user_id, self.user_name, self.set_password(), self.user_class, self.user_class_code, self.user_phone, self.user_email)
            print (sql)
            self.conn.execute(sql) 
        except MySQLError:
            self.conn.rollback()
            return False
        
        self.conn.commit()
        return True
    
    def delete_user(self):
        return False
    
    def login(self):

        sql = "SELECT user_Password \
                FROM User\
                WHERE user_Id='"+ self.user_id + "'"
                
        
        password_list = self.conn.executeOne(sql)
        
        if password_list is not None:
            login_check = self.check_password(password_list['user_Password'].decode('utf-8', 'ignore'))
            
            self.conn.close()
            
            if login_check:
                return True
            
        return False

# if __name__ == '__main__':
#     test = User('bong', 'bong')
#     test.create_user()
#     test.login()
    
    