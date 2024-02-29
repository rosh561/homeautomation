"""
Flask Documentation:     https://flask.palletsprojects.com/
Jinja2 Documentation:    https://jinja.palletsprojects.com/
Werkzeug Documentation:  https://werkzeug.palletsprojects.com/
This file creates your application.
"""

# from crypt import methods
import site 
import json

from app import app, Config,  mongo, Mqtt
from flask import escape, render_template, request, jsonify, send_file, redirect, make_response, send_from_directory 
from json import dumps, loads 
from werkzeug.utils import secure_filename
from datetime import datetime,timedelta, timezone
from os import getcwd
from os.path import join, exists
from time import time, ctime
from math import floor
  



#####################################
#   Routing for your application    #
#####################################


# 1. CREATE ROUTE FOR '/api/set/combination'
@app.route('/api/set/combination/<passcode>', methods=['POST'])
def SetCombinationtest(passcode):
    if request.method == 'POST':
        try:
        
            FourDigitpasscode = int(passcode)
            if  len(passcode) == 4 and type(FourDigitpasscode) == int :
             update = mongo.UpdatePasscode(passcode)   
            if update:
                return jsonify({"status": "complete", "data": "complete"})
            
        except Exception as e:
             print(f"SetCombination error: f{str(e)}")  
             return jsonify({"status": "failed", "data": "failed"})
    
@app.route('/api/set/combination', methods=['POST'])
def SetCombination():
    if request.method == 'POST':
        try:
            
            form = request.form
            passcode = escape(form.get("passcode"))
            
            FourDigitpasscode = int(passcode)
            if  len(passcode) == 4 and type(FourDigitpasscode) == int :
             update = mongo.UpdatePasscode(passcode)   
            if update:
                return jsonify({"status": "complete", "data": "complete"})
            
        except Exception as e:
             print(f"SetCombination error: f{str(e)}")  
             return jsonify({"status": "failed", "data": "failed"})
            

    
# 2. CREATE ROUTE FOR '/api/check/combination'
@app.route('/api/check/combination/<passcode>', methods=['POST'])
def Check_Combinationtest(passcode):
    if request.method == 'POST':
        try:
            
            result = mongo.CheckPasscode(passcode)
            if result:
                return jsonify({"status": "complete", "data": "complete"})
            else:
                return jsonify({"status": "failed", "data": "failed"})
                
        except Exception as e:
            print(f"Check_Combination error: f{str(e)}") 
            
            
@app.route('/api/check/combination', methods=['POST'])
def Check_Combination():
    if request.method == 'POST':
        try:
             
            form = request.form
            passcode = escape(form.get("passcode"))
            print(passcode)
            result = mongo.CheckPasscode(passcode)
            if result:
                return jsonify({"status": "complete", "data": "complete"})
            else:
                return jsonify({"status": "failed", "data": "failed"})
                
        except Exception as e:
            print(f"Check_Combination error: f{str(e)}") 
            


# 3. CREATE ROUTE FOR '/api/update'
@app.route('/api/update',methods=["POST"])  
def update_data():
    '''Saves a file to the uploads folder'''
    
    if request.method == "POST" and request.get_json():
        try:
            
            jsonDoc= request.get_json()

            timestamp = datetime.now().timestamp()
            timestamp = floor(timestamp)
            jsonDoc['timestamp'] = timestamp
            Mqtt.publish("620142646",json.dumps(jsonDoc))
            print(f"MQTT; {jsonDoc}")
            
            update = mongo.addUpdate(jsonDoc)
            if update:
                return jsonify({"status":"complete", "data":"complete" })
    
        except Exception as e:
            msg = str(e)
        print (f"Update Error: {msg}")
        return jsonify({"status":"failed", "data":"failed" })



   
# 4. CREATE ROUTE FOR '/api/reserve/<start>/<end>'
@app.route('/api/reserve/<start>/<end>', methods=['GET']) 
def get_all(start,end):   
    '''RETURNS ALL THE DATA FROM THE DATABASE THAT EXIST IN BETWEEN THE START AND END TIMESTAMPS'''
   
    if request.method == "GET":
        '''Add your code here to complete this route'''

        try:          
            num1 = int(start)
            num2 = int(end)
            data = mongo.getAllInRange(num1,num2)
            if data:
                return jsonify({"status":"found","data": data})
            
        except Exception as e:
            print(f"get_all error: f{str(e)}")  
    # FILE DATA NOT EXIST              
    return jsonify({"status":"not found","data":0})

# 5. CREATE ROUTE FOR '/api/avg/<start>/<end>'
@app.route('/api/avg/<start>/<end>', methods=['GET']) 
def get_reserve_avg(start,end):   
    '''RETURNS AVG FOR RESERVE. THAT FALLS WITHIN THE START AND END DATE RANGE'''
   
    if request.method == "GET": 
        '''Add your code here to complete this route'''
        try:          
            num1 = int(start)
            num2 = int(end)
            data = mongo.Reserve_AVG(num1,num2)
            if data:
                return jsonify({"status":"found","data": data})
            
        except Exception as e:
            print(f"get_reserve_avg error: f{str(e)}")  

    # FILE DATA NOT EXIST
    return jsonify({"status":"not found","data":0})


   






@app.route('/api/file/get/<filename>', methods=['GET']) 
def get_images(filename):   
    '''Returns requested file from uploads folder'''
   
    if request.method == "GET":
        directory   = join( getcwd(), Config.UPLOADS_FOLDER) 
        filePath    = join( getcwd(), Config.UPLOADS_FOLDER, filename) 

        # RETURN FILE IF IT EXISTS IN FOLDER
        if exists(filePath):        
            return send_from_directory(directory, filename)
        
        # FILE DOES NOT EXIST
        return jsonify({"status":"file not found"}), 404


@app.route('/api/file/upload',methods=["POST"])  
def upload():
    '''Saves a file to the uploads folder'''
    
    if request.method == "POST": 
        file     = request.files['file']
        filename = secure_filename(file.filename)
        file.save(join(getcwd(),Config.UPLOADS_FOLDER , filename))
        return jsonify({"status":"File upload successful", "filename":f"{filename}" })

 


###############################################################
# The functions below should be applicable to all Flask apps. #
###############################################################


@app.after_request
def add_header(response):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also tell the browser not to cache the rendered page. If we wanted
    to we could change max-age to 600 seconds which would be 10 minutes.
    """
    response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
    response.headers['Cache-Control'] = 'public, max-age=0'
    return response

@app.errorhandler(405)
def page_not_found(error):
    """Custom 404 page."""    
    return jsonify({"status": 404}), 404



