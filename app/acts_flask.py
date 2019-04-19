from __future__ import print_function
from multiprocessing import Value
from flask import Flask, render_template, request, json, jsonify
import mysql.connector
import hashlib
from datetime import datetime
from dateutil.parser import parse
import types
import base64
import re
import requests

import sys
app = Flask(__name__, static_url_path='/static')

mydb = mysql.connector.connect(host ="db", port = 3306, user = 'root', password = 'root', database = 'selflessacts1')
mycursor = mydb.cursor(buffered=True)
reqcount=Value('i',0)


@app.route(/api/v1/_health, methods=['GET'])
def healthcheck():
    if(mydb.is_connected()):
        response=app.response_class(response=json.dumps({}),status=200,mimetype='application/json')
    else:
        response=app.response_class(response=json.dumps({}),status=500,mimetype='application/json')
    return response



@app.route("/api/v1/_count", methods=['GET'])
def reqcounter():
    with reqcount.get_lock():
        if request.method== 'GET':
            response = app.response_class(response=json.dumps([reqcount.value]), status=200, mimetype='application/json')    
        elif request.method=='POST':
            response = app.response_class(response=json.dumps({}), status=405, mimetype='application/json')
        return response


@app.route("/api/v1/_count", methods=['DELETE'])
def reqcounter1():
    with reqcount.get_lock():
        if request.method== 'DELETE':
            reqcount.value=0
            response = app.response_class(response=json.dumps({}), status=200, mimetype='application/json')      
        elif request.method=='POST':
            response = app.response_class(response=json.dumps({}), status=405, mimetype='application/json')
        return response


#Home page
@app.route('/')
def index():	
    return render_template('Index.html'), 200


#list all categories
@app.route('/api/v1/categories', methods = ['GET'])
def listallcat():
    with reqcount.get_lock():
        reqcount.value=reqcount.value+1
        print("alert listallcatcount acts",reqcount,file=sys.stderr)
        if request.method == 'GET':
            cat = mycursor.execute("SELECT category.catname, category.catcount FROM category ")
            cat = mycursor.fetchall()
            print(cat)
            cat1={}
            if(len(cat)):
                for i in range(len(cat)):
                    cat1[cat[i][0]]=cat[i][1]
                return jsonify(cat1),200
            else:  
                response = app.response_class(response=json.dumps({}), status=204, mimetype='application/json') 
        else:
            response = app.response_class(response=json.dumps({}), status=405, mimetype='application/json')
        return response            

#Add a category
@app.route('/api/v1/categories', methods = ['POST'])
def addcat():
    with reqcount.get_lock():
        reqcount.value=reqcount.value+1
        print("alert countaddcat acts",reqcount,file=sys.stderr)
        if request.method == 'POST':
            content = request.get_json()
            print(content)
            cat = content[0]
            sql= "SELECT catname FROM category WHERE catname=%s"
            rows = mycursor.execute(sql, (cat, ))
            rows = mycursor.fetchone()
            jsonify(rows)
            if(rows):
                response = app.response_class(response=json.dumps({}), status=400, mimetype='application/json')
            else:
                cat3 = "INSERT INTO category (catname,catcount) VALUES(%s,0)"
                mycursor.execute(cat3, (cat, ))
                mydb.commit()
                response = app.response_class(response=json.dumps({}), status=201, mimetype='application/json') 
        else:
            response = app.response_class(response=json.dumps({}), status=405, mimetype='application/json')
        return response         

#Remove a category
@app.route('/api/v1/categories/<categoryName>', methods = ['DELETE'])
def removeacat(categoryName):
    with reqcount.get_lock():
        print("alert countremcatgory acts ",reqcount,file=sys.stderr)
        if request.method == 'DELETE':
            if(categoryName):
                mycursor.execute("SELECT catname FROM category where catname = %s", (categoryName, ))
                n = mycursor.fetchone()
                jsonify(n)
                if(n):
                    cat = mycursor.execute("SELECT catno FROM category where catname = %s", (categoryName, ))
                    cat = mycursor.fetchall()
                    mycursor.execute("DELETE FROM acts where catno1 in (Select catno From category WHERE catname = %s)", (categoryName, ))
                    mycursor.execute("DELETE FROM category where catname = %s", (categoryName, ))
                    mydb.commit()
                    response = app.response_class(response=json.dumps({}), status=200, mimetype='application/json')
                else:
                    response = app.response_class(response=json.dumps({}), status=400, mimetype='application/json')
            else:
                return app.response_class(response=json.dumps({}), status=400, mimetype='application/json')                        
        else:
            response = app.response_class(response=json.dumps({}), status=405, mimetype='application/json')
        return response    
    
#List acts of categories(<100)
@app.route('/api/v1/categories/<categoryName>/acts', methods = ['GET'])
def listactscat(categoryName):
    with reqcount.get_lock():
        reqcount.value=reqcount.value+1
        print("alert countactscat acts",reqcount,file=sys.stderr)
        if request.method == 'GET':
            if(categoryName):
                cat3 = mycursor.execute("SELECT * FROM acts,category WHERE acts.catno1 = category.catno AND category.catname = %s ORDER BY times DESC", (categoryName, ))
                cat3 = mycursor.fetchall()
                jsonify(cat3)
                print(cat3)
                cat4=[]
                if(cat3):
                    for i in range(len(cat3)):
                        cat4.append({"actId":cat3[i][0],"username":cat3[i][4],"timestamp":cat3[i][7],"caption":cat3[i][3],"upvotes":cat3[i][1],"imgB64":cat3[i][6]})
                    if(cat4 and len(cat4) > 100):                          ##Error
                        response = app.response_class(response=json.dumps({}), status=413, mimetype='application/json')
                    else:    
                        response = app.response_class(response=json.dumps(cat4), status=200, mimetype='application/json')
                else:  
                    response = app.response_class(response=json.dumps({}), status=204, mimetype='application/json') 
                
        else:
            response = app.response_class(response=json.dumps({}), status=405, mimetype='application/json')
        return response 
   

#list # acts of a category
@app.route('/api/v1/categories/<categoryName>/acts/size', methods = ['GET'])
def listnoactscat(categoryName):
    with reqcount.get_lock():
        reqcount.value=reqcount.value+1
        print("alert countgetcat acts",reqcount,file=sys.stderr)
        if request.method == 'GET':
            if(categoryName):
                mycursor.execute("SELECT  COUNT(acts.actid) FROM acts,category WHERE category.catname = %s AND category.catno=acts.catno1", (categoryName, ))
                cat8 = mycursor.fetchall()
                print(cat8)
                if(cat8):
                    #return cat8
                    #cat1 = [dict(zip([key[0] for key in mycursor.description], row)) for row in cat8]
                    response = app.response_class(response=json.dumps([cat8[0][0]]), status=200, mimetype='application/json')
                    #return render_template('Signup.html'), 200 #204
                else:  
                    response = app.response_class(response=json.dumps({}), status=204, mimetype='application/json') 
                    #return render_template('Signup.html'), 200 #204
        else:
            response = app.response_class(response=json.dumps({}), status=405, mimetype='application/json')
        return response
        #return render_template('Signup.html'), 200 #204

#return # acts for a category in given range
@app.route('/api/v1/categories/<categoryName>/acts?start=<startRange>&end=<endRange>', methods = ['GET'])
def noactcatrange(categoryName):
    with reqcount.get_lock():
        reqcount.value=reqcount.value+1
        print("alert countcatran acts",reqcount,file=sys.stderr)
        if request.method == 'GET':
            startRange = request.args['start']
            endRange = request.args['end']
            #startRange = int(startRange)
            #endRange = int(endRange)
            print('HI')
            if(categoryName, (startRange >= 1), endRange):
                cnt = mycursor.execute("SELECT COUNT(*) FROM acts WHERE acts.catno1 = category.catno AND category.catname = %s", (categoryName, ))
                cnt = mycursor.fetchone()
                #cnt = jsonify(cnt)
                if(cnt[0] <= endRange):
                    cat6 = mycursor.execute("SELECT * FROM acts WHERE acts.catno1 = category.catno AND category.catname = %s GROUP BY catno1 HAVING COUNT(*) >= %s AND COUNT(*) <= %s ORDER BY times DESC", (categoryName, startRange, endRange, ))
                    cat6 = mycursor.fetchall()
                    if(cat6):   
                        cat7 = [dict(zip([key1[0] for key1 in mycursor.description], row1)) for row1 in cat6]        
                        response = app.response_class(response=json.dumps({'':cat7}), status=200, mimetype='application/json')
                    else:  
                        response = app.response_class(response=json.dumps({}), status=204, mimetype='application/json') 
                        #return render_template('Signup.html'), 200 #204
        else:
            response = app.response_class(response=json.dumps({}), status=405, mimetype='application/json')
        return response
        #return render_template('Signup.html'), 200 #204,413

#Upvote an Act
@app.route('/api/v1/acts/upvote', methods = ['POST'])
def upvoteact():
    with reqcount.get_lock():
        reqcount.value=reqcount.value+1
        print("alert countrem acts",reqcount,file=sys.stderr)
        if request.method == 'POST':
            content1 = request.get_json()
            actid = content1[0]
            mycursor.execute("SELECT votes FROM acts WHERE actid = %s", (actid, ))
            n = mycursor.fetchone()
            if(n):
                votes = n[0] + 1
                votes = int(votes)
                cat4 = "UPDATE acts SET votes = %s WHERE actid = %s"
                mycursor.execute(cat4, (votes, actid, ))
                mydb.commit()
                response = app.response_class(response=json.dumps({}), status=200, mimetype='application/json')
            else:
                response = app.response_class(response=json.dumps({}), status=400, mimetype='application/json')       
        else:
            response = app.response_class(response=json.dumps({}), status=405, mimetype='application/json')
        return response    

#Remove an act
@app.route('/api/v1/acts/<actid>', methods = ['DELETE'])
def removeact(actid):
    with reqcount.get_lock():
        reqcount.value=reqcount.value+1
        print("alert countrem acts",reqcount,file=sys.stderr)
        if request.method == 'DELETE':
            actid = int(actid)
            mycursor.execute("SELECT actid FROM acts WHERE actid = %s", (actid, ))
            id = mycursor.fetchone() 
            if(id and len(id)>0 and id[0] == actid):
                mycursor.execute("DELETE FROM acts where actid = %s", (actid, ))
                mydb.commit()
                response = app.response_class(response=json.dumps({}), status=200, mimetype='application/json')
            else:
                response = app.response_class(response=json.dumps({}), status=400, mimetype='application/json') 
        else:
            response = app.response_class(response=json.dumps({}), status=405, mimetype='application/json')
        return response
        #return render_template('Signup.html'), 200




#Upload an Act
@app.route('/api/v1/acts', methods = ['POST'])
def uploadact():
    with reqcount.get_lock():
        reqcount.value=reqcount.value+1
        print("alert countupload acts",reqcount,file=sys.stderr)
        if request.method == 'POST':
            content = request.get_json()
            cat = content['categoryName']
            uname=content['username']
            acid=content['actId']
            print(content['categoryName'])
            try:
                print(content['upvotes'])
                response=app.response_class(response=json.dumps({}), status=400, mimetype='application/json')
                return response
            except:
                cat1=mycursor.execute("SELECT catno FROM category WHERE category.catname=%s", (cat, ))
                cat1=mycursor.fetchone()
                uarr=requests.get('http://3.83.128.61:80/api/v1/users').content
                uarr=json.loads(uarr)
                #mycursor.execute("SELECT username FROM users WHERE users.username=%s", (uname, ))
                #unamecheck=mycursor.fetchone()
                unamecheck=False
                for i in range(len(uarr)):
                    if(uarr[i]==content['username']):
                        unamecheck=True
                        break
                mycursor.execute("SELECT actid FROM acts WHERE actid=%s", (acid, ))
                acidcheck=mycursor.fetchone()
                print("cat1",len(cat1))
                print("unamecheck")
                print("acidcheck",type(acidcheck))
                imgcheck=re.match("^([A-Za-z0-9+/]{4})*([A-Za-z0-9+/]{3}=|[A-Za-z0-9+/]{2}==)?$",content['imgB64'])
                try:
                    dateobj=datetime.strptime(content['timestamp'],"%d-%m-%Y:%S-%M-%H")
                except:
                    response=app.response_class(response=json.dumps({}), status=400, mimetype='application/json')
                    return response
                if(len(cat1)==1 and unamecheck and acidcheck==None and imgcheck):
                    print(cat1)
                    cat3 = "INSERT INTO acts (comments,actid,caption,uname,catno1,imgpath,times,votes) VALUES(%s,%s,%s,%s,%s,%s,%s,%s)"
                    mycursor.execute(cat3, ('',content['actId'],content['caption'],content['username'],cat1[0],content['imgB64'],datetime.strptime(content['timestamp'],"%d-%m-%Y:%S-%M-%H")  ,0))
                    cat4= mycursor.execute("UPDATE category SET catcount=catcount +1 WHERE category.catname=%s",(content['categoryName'],))
                    mydb.commit()
                    response = app.response_class(response=json.dumps({}), status=201, mimetype='application/json')
                    #return render_template('Signup.html'), 201
                else:
                    response = app.response_class(response=json.dumps({}), status=400, mimetype='application/json')
        else:
            response = app.response_class(response=json.dumps({}), status=405, mimetype='application/json')
        return response
        #return render_template('Signup.html'), 201



@app.route('/api/v1/acts/count',methods=['GET'])
def getcountacts():
    with reqcount.get_lock():
        reqcount.value=reqcount.value+1
        print("alert countgetacts acts",reqcount,file=sys.stderr)
        if request.method!='GET':
            response=app.response_class(response=json.dumps({}), status=405, mimetype='application/json')
        else:
            mycursor.execute("SELECT actid FROM acts")
            actdis=mycursor.fetchall()
            print("hello")
            print(actdis)
            print("wow",len(actdis))
            response=app.response_class(response=json.dumps([actdis]), status=200, mimetype='application/json')
        return response



def isBase64(s):
    try:
        return base64.b64encode(base64.b64decode(s)) == s
    except Exception:
        return False



if __name__ == '__main__':
    app.run(host='0.0.0.0',port='80',debug=True)

