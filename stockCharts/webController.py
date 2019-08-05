'''
Created on 2019. 6. 25.

@author: Harry
'''
import os
import json
import configparser
import urllib.request

from flask import Flask, render_template, request, jsonify, redirect, session, url_for
from bs4 import BeautifulSoup
from module import dbModule
from dao.userDAO import User
from module.sessionModule import redis_session

config = configparser.ConfigParser()
config.read(os.getcwd() + "/conf/URLinfo.conf")

key = config['SecretKey']

app = Flask(__name__)
app.secret_key = key['secret_key']

@app.route('/getAuto', methods=['POST', 'GET'])
def getAutoComplete():

    keyword = None
    
    if request.method == "POST":
        
        url = config['KakaoURL']
        keyword = urllib.parse.quote(request.json['keyword'])
        auto_url = url['autoPage'] + keyword
        data = json.load(urllib.request.urlopen(auto_url))
        
        app.logger.info("::::::: Kakao scraping url ::::::: \n %s", auto_url)
        app.logger.info("::::::: Kakao scraping data ::::::: \n %s", data)
        for v in data['suggestItems']:
            app.logger.info(v['code'] + " == " + v['name'] + " == " + v['displayedSubtype'] + " == " + v['displayedCode'])
    
        return jsonify(data['suggestItems'])
            
    return "error"

@app.route('/getCurrentValue', methods=['POST', 'GET'])
def getCurrentValue():
    
    requestJsonData = request.json
    
    db_class = dbModule.Database()
    userId = check_session()
    
    if userId is None:
        app.logger.info("::::::: Session End ::::::: \n")
        return 'End'
    
    app.logger.info("::::::: getCurrentValue ::::::: \n %s", userId)
    sql = "INSERT INTO UserStockList (user_Id, list_Code, list_Acode, list_Name, status, date) \
            SELECT user_Id, '"+ requestJsonData['displayedCode'] +"' as 'list_Code', '"+ requestJsonData['id'] +"' as 'list_Acode', '"+ requestJsonData['value'] + "' as 'list_Name', \
            'I' as 'status', NOW() as 'date' \
            FROM User WHERE user_Id = '" + userId + "'"
     
    print(sql) 
    
    db_class.execute(sql)
    db_class.commit()
     
    db_class.close()
    
    return generateChartDivTag(requestJsonData)


@app.route('/deleteChartImage', methods=['POST', 'GET'])
def deleteStock():
    requestJsonData = request.json
    
    db_class = dbModule.Database()
    userId = check_session()
    
    if userId is None:
        app.logger.info("::::::: Session End ::::::: \n")
        return 'End'
    
#     sql = "DELETE FROM UserStockList \
#             WHERE user_Id='" + userId + "' AND list_Acode='" + requestJsonData['id'] + "'"

    sql = "UPDATE UserStockList \
            SET status='D'\
            WHERE user_Id='" + userId + "' AND list_Acode='" + requestJsonData['id'] + "'"
    
    db_class.execute(sql)
    db_class.commit()
     
    db_class.close()    
    
    return ""


@app.route('/login', methods=['POST'])
def login():
    
    user_id = request.form['no']
    password = request.form['password']
    
    if User(user_id, password).login() is False :
        return render_template('login.html', login_fail=1)
    
    session_key = redis_session().save_session(user_id)
    
    session['session_key'] = session_key
    
    app.logger.info("::::::: login success! ::::::: \n")
    
    return redirect(url_for('home'))
    
    
@app.route('/logout', methods=['POST', 'GET'])
def logout():
    if 'session_key' in session:
        del session['session_key']
        
    app.logger.info("::::::: loginout success! ::::::: \n")
    return 'True'
    
@app.route('/')
def home():
    
    userId = check_session()
    
    if userId is None:
        app.logger.info("::::::: Session End ::::::: \n")
        return render_template('login.html')
    
    db_class = dbModule.Database()
    
    sql = "SELECT list_Code as displayedCode, list_Name as value, list_Acode as id \
            FROM UserStockList \
            WHERE user_Id = '" + userId + "' AND status='I'"

    row = db_class.executeAll(sql)
    tags = ''

    for r in row:
        r['displayedCode'] = r['displayedCode'].decode('utf8', 'ignore')
        r['value'] = r['value'].decode('utf8', 'ignore')
        r['id'] = r['id'].decode('utf8', 'ignore')
        tags += generateChartDivTag(r)
    
    app.logger.info("::::::: result for UserStockList table ::::::: \n %s", row)
    app.logger.info("::::::: result for Generated Tags ::::::: \n %s", tags)
    
    db_class.close()
    return render_template('home.html', resultData = tags)

def scrapingInfo(code):
    
    url = config['NaverURL']
    scrap_url = url['stockPage'] + code
    html_data = urllib.request.urlopen(scrap_url)
    bsObject = BeautifulSoup(html_data.read().decode('cp949', 'ignore'), "html.parser")
    soup = bsObject.find('div', {'class':"today"})
    app.logger.info("::::::: Naver scraping url ::::::: \n %s", scrap_url)
    app.logger.info("::::::: Naver scraping data ::::::: \n %s", soup)
    
    json_name = ["current", "gap", "percent", "upOrdown", "symbol"]
    json_name_sam = ["current", "gap", "percent", "upOrdown"]
    
    result = []
    values = []
    
    if soup != None:
        for v in soup.select('.blind'):
            app.logger.info("::::::: Naver soup blind ::::::: -> %s", v.text)
            values.append(v.text)
        
        for c in soup.select('.ico'):
            app.logger.info("::::::: Naver soup ico ::::::: -> %s", c.text)
            values.append(c.text)
        
        if (len(values) == 4) :
            json_name = json_name_sam;
        
        for i in range(0, len(json_name)):
            result.append({json_name[i]:values[i]})
            app.logger.info("::::::: Naver same price to yesterday json_name_sam[i] ::::::: -> %s", json_name[i])
            app.logger.info("::::::: Naver same price to yesterday values[i] ::::::: -> %s", values[i])
        
        app.logger.info("::::::: extracted data from Naver ::::::: \n %s", result)    
    
    
    return result;

def generateChartDivTag(info):
    
    data = scrapingInfo(info['displayedCode'])
    kakao_url = config['KakaoURL']
    kakao_url = kakao_url['dayChartPage']
    
    tag = "<div class='col-sm-5 col-md-4 col-lg-3 each-chart " + info['id'] + "'> \
                <div class='chart-img'> \
                    <img src='" + kakao_url + info['id'] + ".png' class='img-responsive' id='img-" + info['displayedCode'] + "'> \
                </div> \
                <div class='chart-info'> \
                    <div class='info-name'>" + info['value'] + "<span class='info-name-code'> (" + info['displayedCode'] +") </span>\
                    </div>"
                
    if len(data) > 0:
        arrow = 'fa fa-minus'
        style = "black"
        symbol = '.'
        
        if len(data) > 4:
            symbol = data[4]['symbol']
            if symbol == '+' :
                arrow = 'fa fa-caret-up'
                style = 'red'
            else:
                arrow = 'fa fa-caret-down'
                style = 'blue'
        
        tag += "<span class='info-price'>" + data[0]['current'] + " </span> <br>\
                    <span class='info-fluctuation' style='color:"+ style +"'><i class='" + arrow + "' style='font-size:1.8rem'></i>  " + data[1]['gap'] + " " + symbol + data[2]['percent'] + "% </span>"
    
    tag += "<div class='chart-buttons'> \
            <button class='btn btn-mini btn-danger chart-img-remove' value='" + info['id'] + "' onclick='deleteStockImg(this)'>X</button> \
                    </div> \
                </div> \
            </div>"
            
    app.logger.info("::::::: generated Tag ::::::: \n %s", tag)

    return tag

def check_session():
    if 'session_key' not in session:
        return None
    
    session_key = session['session_key']
    user_id = redis_session().open_session(session_key)
    
    if user_id is None:
        del session['session_key']
        return None
        
    return user_id.decode('utf8', 'ignore')

if __name__ == '__main__':
    app.run('0.0.0.0',port='5000', debug=True)
#     app.run(debug=True)
#     app.run('192.168.123.131',port='5000', debug=True)