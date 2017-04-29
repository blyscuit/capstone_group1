# ======================== Import & Setup ========================

import os
from flask import Flask, request, jsonify, make_response, request, current_app, render_template, redirect, url_for, send_from_directory, session, abort, flash
from datetime import timedelta
from werkzeug import secure_filename
from flaskext.mysql import MySQL
from flask_login import LoginManager, UserMixin, login_required
from functools import update_wrapper
from flask_cors import CORS, cross_origin
import json
import collections
import uuid
from wand.image import Image
from random import randint
# from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__, static_url_path = "", static_folder = "")
# app.config['MYSQL_DATABASE_HOST'] = 'localhost'
app.config['MYSQL_DATABASE_HOST'] = 'snowywords2.ddns.net'
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = '0904'
app.config['SERVER_NAME'] = 'localhost:5000'
# app.config['SERVER_NAME'] = 'snowywords2.ddns.net:5000'

# app.config['MYSQL_DATABASE_HOST'] = 'localhost'
# app.config['MYSQL_DATABASE_USER'] = 'root'
# app.config['MYSQL_DATABASE_PASSWORD'] = 'root'

app.config['MYSQL_DATABASE_DB'] = 'kaidee'
app.config['UPLOAD_FOLDER'] = 'upload/'
app.config['ALLOWED_EXTENSIONS'] = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

app.config.update(dict(
    # DATABASE=os.path.join(app.root_path, 'flaskr.db'),
    DEBUG=True,
    # SECRET_KEY='development key',
    USERNAME='admin',
    PASSWORD='default'
))
app.config.from_envvar('KAIDEEV_SETTINGS', silent=True)

mysql = MySQL(app)
CORS(app)
login_manager = LoginManager()
login_manager.init_app(app)


# ========================= Default Route =========================

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/<path:path>')
def static_file(path):
    return app.send_static_file(path)


# ========================= Authentication =========================

@app.route('/login', methods=['POST'])
def login():
    username = None
    password = None
    userID = None
    cur = mysql.get_db().cursor()
    cur2 = mysql.get_db().cursor()
    query_string = "SELECT Email, Password, UserID FROM kaidee.user WHERE Email =" + "\'" +request.form['username']+"\'"
    cur.execute(query_string)
    data = cur.fetchall()
    if data == ():
        print ("User not found")
        return ('This user does not exist')
    for row in data:
        username = row[0]
        password = row[1]
        userID = row[2]
    query_string = "SELECT UserID, Firstname, Lastname, Email, Postcode, Display_name, LevelID_u AS VLevel, ProfilePic \
                    FROM kaidee.user WHERE UserID = " + str(userID)
    cur.execute(query_string)
    columns = [column[0] for column in cur.description]
    results = []
    columns.append('Phone')
    columns.append('Social')
    for row in cur.fetchall():
        FAQID = row[0]
        row = list(row)
        query_string_2 = "SELECT Phone_no FROM phone WHERE UserID_p = " + str(userID)
        cur2.execute(query_string_2)
        phoneNo = []
        for i in cur2.fetchall():
            phoneNo.append(i[0])
        row.append(phoneNo)
        query_string_2 = "SELECT SocialID, Type FROM social WHERE UserID_s = " + str(userID)
        cur2.execute(query_string_2)
        data = cur2.fetchall()
        columns2 = getSocialType([r[1] for r in data])
        social = []
        row2 = []
        for i in data:
            row2.append(i[0])
        social.append(dict(zip(columns2, row2)))
        row.append(social[0])
        results.append(dict(zip(columns, row)))
    if request.form['password'] == str(password) and request.form['username'] == str(username):
        session['logged_in'] = True
        if len(results)>0:
            session['udata'] = json.dumps(results)
            if str(username) == "admin@admin.com":
                print("***********************************************************")
                return redirect('/verify_admin')
            else:
                return redirect('/')
    else:
        flash('wrong password!')
        return "the password is fucking wrongggggg"


@app.route("/logout")
def logout():
    session['logged_in'] = False
    return redirect('/')


# ========================= User Information =========================

@app.route('/users', methods=['GET'])
def users():
    if not session.get('logged_in'):
        print('Not logged in!')
        return ('Cannot load data: user is not logged in')
    userID = json.loads(session.get('udata'))[0].get('UserID')
    cur = mysql.get_db().cursor()
    cur2 = mysql.get_db().cursor()
    query_string = "SELECT Firstname, Lastname, Email, Postcode, Display_name, LevelID_u AS VLevel, ProfilePic \
                    FROM kaidee.user WHERE UserID = " + str(userID)
    cur.execute(query_string)
    columns = [column[0] for column in cur.description]
    results = []
    columns.append('Phone')
    columns.append('Social')
    for row in cur.fetchall():
        FAQID = row[0]
        row = list(row)
        query_string_2 = "SELECT Phone_no FROM phone WHERE UserID_p = " + str(userID)
        cur2.execute(query_string_2)
        phoneNo = []
        for i in cur2.fetchall():
            phoneNo.append(i[0])
        row.append(phoneNo)
        query_string_2 = "SELECT SocialID, Type FROM social WHERE UserID_s = " + str(userID)
        cur2.execute(query_string_2)
        data = cur2.fetchall()
        columns2 = getSocialType([r[1] for r in data])
        social = []
        row2 = []
        for i in data:
            row2.append(i[0])
        social.append(dict(zip(columns2, row2)))
        row.append(social[0])
        results.append(dict(zip(columns, row)))
    if len(results)>0:
        return jsonify(results)
    else:
        print('No data found at the index')
        return ('404')


@app.route('/session_data', methods=['GET'])
def session_data():
    if session.get('logged_in'):
        data = json.loads(session.get('udata'))
        data = data[0]
        return jsonify(data)
    else:
        print ("Not logged in!")
        return ('404')


# ========================= FAQ =========================

@app.route('/faq/all', methods=['GET'])
def get_faq():
    cur = mysql.get_db().cursor()
    cur2 = mysql.get_db().cursor()
    query_string = "SELECT * FROM faq "
    cur.execute(query_string)
    columns = [column[0] for column in cur.description]
    results = []
    columns.append('FAQImage')
    for row in cur.fetchall():
        FAQID = row[0]
        row = list(row)
        query_string_2 = "SELECT FAQImage FROM faqpicture WHERE FAQID_fp=" + str(FAQID)
        cur2.execute(query_string_2)
        images = []
        for i in cur2.fetchall():
            images.append(i[0])
        row.append(images)
        results.append(dict(zip(columns, row)))
    if len(results)>0:
        return jsonify(results)
    else:
        print('No data found at the index')
        return ('404')


@app.route('/faqfeedback', methods=['POST'])
def faqfeedback():
    data = request.get_json()
    db = mysql.get_db()
    cur = db.cursor()
    try:
        for faqID in data.get('faqID'):
            query_string = "INSERT INTO viewhistory (UserID_vh, FAQID_vh, Vote_status, Timestamp) \
                            VALUES (" + str(data.get('userID')) + ", " + str(faqID) + ", " + \
                            str(data.get('vote')) + ", " + str(data.get('timestamp')) + ")"
            cur.execute(query_string)
            db.commit()
        print("Insert data success")
        return ('201')
    except:
        print("Insert data failed")
        db.rollback()
        return ('403')


# ========================= Product Information =========================

@app.route('/browse_product', methods=['GET'])
def browse_product():
    cur = mysql.get_db().cursor()
    cur2 = mysql.get_db().cursor()
    query_string = "SELECT ItemID, Name, Price, Postcode, LevelID_u \
                   FROM item i, user u \
                   WHERE i.UserID_i = u.UserID \
                   ORDER BY ItemID ASC"
    cur.execute(query_string)
    columns = [column[0] for column in cur.description]
    results = []
    columns.append('ItemImage')
    for row in cur.fetchall():
        itemID = row[0]
        row = list(row)
        query_string_2 = "SELECT ItemImage FROM itempicture WHERE ItemID_ip=" + str(itemID)
        cur2.execute(query_string_2)
        images = []
        for i in cur2.fetchall():
            images.append(i[0])
        row.append(images)
        results.append(dict(zip(columns, row)))
    if len(results)>0:
        return jsonify(results)
    else:
        print('No data found at the index')
        return ('404')


@app.route('/view_product/<int:ItemID>', methods=['GET'])
def view_product(ItemID):
    cur = mysql.get_db().cursor()
    cur2 = mysql.get_db().cursor()
    query_string = "SELECT ItemID, Name, Description, Date, Price, Display_name, Postcode, LevelID_u \
                   FROM item i, user u \
                   WHERE i.ItemID = '{ItemID}' AND i.UserID_i = u.UserID".format(ItemID = ItemID)
    cur.execute(query_string)
    columns = [column[0] for column in cur.description]
    results = []
    columns.append('ItemImage')
    for row in cur.fetchall():
        itemID = row[0]
        row = list(row)
        query_string_2 = "SELECT ItemImage FROM itempicture WHERE ItemID_ip=" + str(itemID)
        cur2.execute(query_string_2)
        images = []
        for i in cur2.fetchall():
            images.append(i[0])
        row.append(images)
        results.append(dict(zip(columns, row)))
    if len(results)>0:
        return jsonify(results)
    else:
        print('No data found at the index')
        return ('404')



# ========================= Chat System =========================

@app.route('/get_deal_list', methods=['GET'])
def get_deal_list():
    if not session.get('logged_in'):
        print('Not logged in!')
        return ('Cannot load data: user is not logged in')
    userID = json.loads(session.get('udata'))[0].get('UserID')
    cur = mysql.get_db().cursor()
    cur2 = mysql.get_db().cursor()
    query_string = "SELECT ItemID, Name AS ItemName, Description AS ItemDescription, Display_name, BuyerID_c AS BuyerID, \
                    SellerID_c AS SellerID, ChatID FROM item i, user u, chat c \
                    WHERE i.ItemID = c.ItemID_c AND u.UserID = " + str(userID) + " AND (c.BuyerID_c = " + str(userID) + " \
                    OR c.SellerID_c = " + str(userID) + ")"
    cur.execute(query_string)
    columns = [column[0] for column in cur.description]
    results = []
    columns.append('ItemImage')
    for row in cur.fetchall():
        itemID = row[0]
        row = list(row)
        query_string_2 = "SELECT ItemImage FROM itempicture WHERE ItemID_ip=" + str(itemID)
        cur2.execute(query_string_2)
        row.append(cur2.fetchall()[0][0])
        results.append(dict(zip(columns, row)))
    if len(results)>0:
        return jsonify(results)
    else:
        print('No data found at the index')
        return ('404')


@app.route('/get_deal_info/<int:ChatID>', methods=['GET'])
def get_deal_info(ChatID):
    if not session.get('logged_in'):
        print('Not logged in!')
        return ('Cannot load data: user is not logged in')
    cur = mysql.get_db().cursor()
    cur2 = mysql.get_db().cursor()
    query_string = "SELECT ItemID, Name AS ItemName, Description AS ItemDescription, BuyerID_c AS BuyerID, SellerID_c AS SellerID, \
                    Display_name, ProfilePic FROM item i, user u, chat c \
                    WHERE c.ChatID = '{ChatID}' AND i.UserID_i = c.SellerID_c AND u.UserID = c.SellerID_c AND c.ItemID_c = i.ItemID".format(ChatID=ChatID)
    cur.execute(query_string)
    columns = [column[0] for column in cur.description]
    results = []
    columns.append('ItemImage')
    for row in cur.fetchall():
        itemID = row[0]
        row = list(row)
        query_string_2 = "SELECT ItemImage FROM itempicture WHERE ItemID_ip=" + str(itemID)
        cur2.execute(query_string_2)
        row.append(cur2.fetchall()[0][0])
        results.append(dict(zip(columns, row)))
    if len(results)>0:
        return jsonify(results)
    else:
        print('No data found at the index')
        return ('404')


@app.route('/get_message_history/<int:ChatID>', methods=['GET'])
def get_message_history(ChatID):
    if not session.get('logged_in'):
        print('Not logged in!')
        return ('Cannot load data: user is not logged in')
    cur = mysql.get_db().cursor()
    query_string = "SELECT * FROM message WHERE ChatID_m = '{ChatID}' ORDER BY MessageID DESC".format(ChatID=ChatID)
    cur.execute(query_string)
    columns = [column[0] for column in cur.description]
    results = []
    for row in cur.fetchall():
        results.append(dict(zip(columns, row)))
    if len(results)>0:
        return jsonify(results)
    else:
        print('No data found at the index')
        return ('404')


@app.route('/get_latest_msg/<int:ChatID>', methods=['GET'])
def get_latest_msg(ChatID):
    if not session.get('logged_in'):
        print('Not logged in!')
        return ('Cannot load data: user is not logged in')
    cur = mysql.get_db().cursor()
    query_string = "SELECT * FROM message WHERE ChatID_m = '{ChatID}' AND IsRead = 0 ORDER BY MessageID DESC".format(ChatID=ChatID)
    cur.execute(query_string)
    columns = [column[0] for column in cur.description]
    results = []
    for row in cur.fetchall():
        results.append(dict(zip(columns, row)))
    if len(results)>0:
        return jsonify(results)
    else:
        print('No data found at the index')
        return ('404')


@app.route('/count_unread/<int:ChatID>', methods=['GET'])
def count_unread(ChatID):
    if not session.get('logged_in'):
        print('Not logged in!')
        return ('Cannot load data: user is not logged in')
    cur = mysql.get_db().cursor()
    query_string = "SELECT COUNT(MessageID) AS UnreadQty, SenderID FROM message \
                    WHERE ChatID_m = '{ChatID}' AND IsRead = 0 GROUP BY SenderID".format(ChatID=ChatID)
    cur.execute(query_string)
    columns = [column[0] for column in cur.description]
    results = []
    for row in cur.fetchall():
        results.append(dict(zip(columns, row)))
    if len(results)>0:
        return jsonify(results)
    else:
        print('No data found at the index')
        return ('404')


@app.route('/send_message', methods=['POST'])
def send_message():
    if not session.get('logged_in'):
        print('Not logged in!')
        return ('Cannot post data: user is not logged in')
    data = request.get_json()
    db = mysql.get_db()
    cur = db.cursor()
    try:
        query_string = "INSERT INTO message (ChatID_m, SenderID, Text, Timestamp) \
                        VALUES (" + str(data.get('chatID')) + ", " + str(data.get('senderID')) + ", \"" + \
                        str(data.get('message')) + "\", " + str(data.get('timestamp')) + ")"
        cur.execute(query_string)
        db.commit()
        print("Insert data success")
        return ('201')
    except:
        print("Insert data failed")
        db.rollback()
        return ('403')


@app.route('/set_as_read', methods=['POST'])
def set_as_read():
    if not session.get('logged_in'):
        print('Not logged in!')
        return ('Cannot post data: user is not logged in')
    userID = json.loads(session.get('udata'))[0].get('UserID')
    data = request.get_json()
    db = mysql.get_db()
    cur = db.cursor()
    try:
        query_string = "UPDATE message SET IsRead = 1 WHERE MessageID = " + str(data.get('messageID'))
        cur.execute(query_string)
        db.commit()
        print("Update data success")
        return ('201')
    except:
        print("Update data failed")
        db.rollback()
        return ('403')


@app.route('/start_chat/<int:itemID>', methods=['GET'])
def start_chat(itemID):
    if not session.get('logged_in'):
        print('Not logged in!')
        return ('Cannot load data: user is not logged in')
    userID = json.loads(session.get('udata'))[0].get('UserID')
    db = mysql.get_db()
    cur = db.cursor()
    query_string = "SELECT ChatID FROM chat WHERE BuyerID_c = " + str(userID) + " AND ItemID_c = " + str(itemID)
    cur.execute(query_string)
    if cur.fetchall() == ():
        print ('Chat does not exist : creating...')
        try:
            query_string = "INSERT INTO chat (ItemID_c, BuyerID_c) VALUES (" + str(itemID) + ", " + str(userID) + ")"
            cur.execute(query_string)
            db.commit()
            print("Create chat success")
        except:
            print("Create chat failed")
            db.rollback()
            return ('403')
    query_string = "SELECT ChatID FROM chat WHERE BuyerID_c = " + str(userID) + " AND ItemID_c = " + str(itemID)
    cur.execute(query_string)
    columns = [column[0] for column in cur.description]
    results = []
    for row in cur.fetchall():
        results.append(dict(zip(columns, row)))
    if len(results)>0:
        return jsonify(results)
    else:
        print('No data found at the index')
        return ('404')


# ========================= User Verification =========================

@app.route('/upload', methods=['POST'])
def upload():
    if not session.get('logged_in'):
        print('Not logged in!')
        return ('Cannot load data: user is not logged in')
    userID = json.loads(session.get('udata'))[0].get('UserID')
    vlevel = request.args.get('vlevel')
    file = request.files['file']
    if not session.get('logged_in'):
        print ("Not logged in")
        return ('Cannot upload: user is not logged in')
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        unique_filename = str(uuid.uuid4()) + '.' + filename.rsplit('.', 1)[1]
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        os.rename(app.config['UPLOAD_FOLDER'] + filename, app.config['UPLOAD_FOLDER'] + unique_filename)
        with Image(filename=app.config['UPLOAD_FOLDER']+unique_filename) as background:
            with Image(filename='watermark.png') as watermark:
                if background.size[0]>background.size[1]:
                    watermark.resize(width=background.size[0], height=background.size[0])
                else:
                    watermark.resize(width=background.size[1], height=background.size[1])
                background.watermark(image=watermark, transparency=0.1)
            background.save(filename = app.config['UPLOAD_FOLDER'] + filename)
        os.replace(app.config['UPLOAD_FOLDER'] + filename, app.config['UPLOAD_FOLDER'] + unique_filename)

        cur = mysql.get_db().cursor()
        db = mysql.get_db()
        url = "http://snowywords2.ddns.net:5000" + str(url_for('uploaded_file', filename = unique_filename))
        query_string = "INSERT INTO verification(Vlevel, VPicture, Status, OTP, UserID_v) \
                        VALUES (" + str(vlevel) + ", \"" + url + "\", 0, " + randomOTP() + ", " + str(userID) +")"
        try:
            cur.execute(query_string)
            db.commit()
            print("Upload success")
        except:
            print("Upload failed")
            db.rollback()

        return redirect('/verification_result')
    else:
        print ('Invalid file type')
        return ('403')


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


@app.route('/get_verification')
def get_verification():
    if not session.get('logged_in'):
        print('Not logged in!')
        return ('Cannot load data: user is not logged in')
    userID = json.loads(session.get('udata'))[0].get('UserID')
    cur = mysql.get_db().cursor()
    cur2 = mysql.get_db().cursor()
    query_string = "SELECT Display_name as Name, LevelID_u as VLevel FROM user WHERE UserID = " + str(userID)
    cur.execute(query_string)
    columns = [column[0] for column in cur.description]
    results = []
    columns.append("VData")
    for row in cur.fetchall():
        row = list(row)
        query_string_2 = "SELECT VLevel, VPicture, Status FROM verification WHERE UserID_v = " + str(userID) + " ORDER BY VLevel"
        cur2.execute(query_string_2)
        columns2 = [column2[0] for column2 in cur2.description]
        results2 = []
        for row2 in cur2.fetchall():
            results2.append(dict(zip(columns2, row2)))
        row.append(results2)
        results.append(dict(zip(columns, row)))
    if len(results)>0:
        return jsonify(results)
    else:
        print('No data found at the index')
        return ('404')


# ========================= Admin Verification =========================

@app.route('/unverified', methods=['GET'])
def getUnverified():
    if not session.get('logged_in'):
        print('Not logged in!')
        return ('Cannot load data: user is not logged in')
    if json.loads(session.get('udata'))[0].get('Email') != "admin@admin.com":
        print('Access Denied')
        return ('Cannot load data: user is unauthorized')
    cur = mysql.get_db().cursor()
    query_string = "SELECT VerificationID, VLevel, VPicture, Status, OTP, UserID_v as UserID FROM kaidee.verification WHERE Status = 0"
    cur.execute(query_string)
    cur.execute(query_string)
    columns = [column[0] for column in cur.description]
    results = []
    for row in cur.fetchall():
        results.append(dict(zip(columns, row)))
    if len(results)>0:
        return jsonify(results)
    else:
        print('No data found at the index')
        return ('404')


@app.route('/verify', methods=['POST'])
def verify():
    if not session.get('logged_in'):
        print('Not logged in!')
        return ('Cannot post data: user is not logged in')
    if json.loads(session.get('udata'))[0].get('Email') != "admin@admin.com":
        print('Access Denied')
        return ('Cannot post data: user is unauthorized')
    data = request.get_json()
    db = mysql.get_db()
    cur = db.cursor()
    try:
        query_string = "UPDATE verification SET status =" +str(data.get('Status')) + " WHERE VerificationID = " + str(data.get('VerificationID'))
        cur.execute(query_string)
        db.commit()
        print("Update data success")
        return ('201')
    except:
        print("Update data failed")
        db.rollback()
        return ('403')


# ========================= Page Hosting =========================

@app.route('/loginpage')
def loginpage():
    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        data = json.loads(session.get('udata'))
        data = data[0]
        return "Hello " + data.get('Display_name') + "! <a href='/logout'>Logout</a>"


# @app.route('/verification_upload')
# def verification_upload():
#     return render_template('verificationUpload.html')


@app.route('/verify_admin')
def verify_admin():
    if not session.get('logged_in'):
        print('Not logged in!')
        return redirect('/loginpage')
    if json.loads(session.get('udata'))[0].get('Email') == "admin@admin.com":
        return render_template('VerifyAdmin.html')
    else:
        print ('Access denied')
        return ('Access Denied')


@app.route('/verification')
def verification():
    if not session.get('logged_in'):
        print('Not logged in!')
        return redirect('/loginpage')
    return render_template('verifyMain.html')


@app.route('/verification_1')
def verification1():
    if not session.get('logged_in'):
        print('Not logged in!')
        return redirect('/loginpage')
    return render_template('verifyLevel1.html')


@app.route('/verification_2')
def verification2():
    if not session.get('logged_in'):
        print('Not logged in!')
        return redirect('/loginpage')
    return render_template('verifyLevel2.html')


@app.route('/verification_3')
def verification3():
    if not session.get('logged_in'):
        print('Not logged in!')
        return redirect('/loginpage')
    return render_template('verifyLevel3.html')


@app.route('/verification_result')
def verification_result():
    if not session.get('logged_in'):
        print('Not logged in!')
        return redirect('/loginpage')
    return render_template('verifyResult.html')


@app.route('/list')
def listpage():
    return render_template('list.htm')


@app.route('/product')
def product():
    print(request.args.get('id'))
    return render_template('Product.html')


@app.route('/help')
def help():
    return render_template('help.html')


@app.route('/faq')
def faq():
    return render_template('faq.html')


@app.route('/upload_sale_1')
def uploadsale1():
    if not session.get('logged_in'):
        print('Not logged in!')
        return redirect('/loginpage')
    return render_template('uploadSale1.html')


@app.route('/upload_sale_2')
def uploadsale2():
    if not session.get('logged_in'):
        print('Not logged in!')
        return redirect('/loginpage')
    return render_template('uploadSale2.html')


@app.route('/upload_sale_3')
def uploadsale3():
    if not session.get('logged_in'):
        print('Not logged in!')
        return redirect('/loginpage')
    return render_template('uploadSale3.html')


@app.route('/upload_sale_4')
def uploadsale4():
    if not session.get('logged_in'):
        print('Not logged in!')
        return redirect('/loginpage')
    return render_template('uploadSale4.html')


@app.route('/upload_sale_5')
def uploadsale5():
    if not session.get('logged_in'):
        print('Not logged in!')
        return redirect('/loginpage')
    return render_template('uploadSale5.html')


@app.route('/upload_sale_6')
def uploadsale6():
    if not session.get('logged_in'):
        print('Not logged in!')
        return redirect('/loginpage')
    return render_template('uploadSale6.html')


# ========================= Error Handler =========================

@app.errorhandler(404)
def page_not_found(error):
    return 'This page does not exist you fuckin dummy', 404


# ========================= Methods =========================

def getSocialType(socialID):
    socialType = []
    print("socialID: " + str(socialID))
    for i in socialID:
        if i == 1:
            socialType.append("Facebook")
        elif i == 2:
            socialType.append("Line")
        elif i == 3:
            socialType.append("Twitter")
    return socialType


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']


def randomOTP():
    n = 4
    return str(''.join(["%s" % randint(0, 9) for num in range(0, n)]))


# ========================= Initiate Server =========================

if __name__ == '__main__':
    app.secret_key = os.urandom(12)
    app.run(host='0.0.0.0', port=5000)
