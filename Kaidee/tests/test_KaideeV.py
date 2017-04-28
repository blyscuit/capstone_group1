# -*- coding: utf-8 -*-
"""
    KaideeV Tests
    ~~~~~~~~~~~~

    Tests the KaideeV application.

    :copyright: (c) 2015 by Armin Ronacher.
    :license: BSD, see LICENSE for more details.
"""

import os
import tempfile
import pytest
from KaideeV import KaideeV
import json
import time


@pytest.fixture
def client(request):
    db_fd, KaideeV.app.config['DATABASE'] = tempfile.mkstemp()
    KaideeV.app.config['TESTING'] = True
    client = KaideeV.app.test_client()
    # with KaideeV.app.app_context():
    #     KaideeV.init_db()
    KaideeV.app.config['MYSQL_DATABASE_HOST'] = 'localhost'
    KaideeV.app.config['MYSQL_DATABASE_USER'] = 'root'
    KaideeV.app.config['MYSQL_DATABASE_PASSWORD'] = 'root'
    KaideeV.app.config['MYSQL_DATABASE_DB'] = 'kaidee'
    def teardown():
        os.close(db_fd)
        os.unlink(KaideeV.app.config['DATABASE'])
    request.addfinalizer(teardown)

    return client

def test_get_user(client):
    rv = client.get('/users/1')
    dic = json.loads(rv.data)
    assert dic[0]['Display_name']
    assert dic[0]['Email']
    assert dic[0]['Firstname']
    assert dic[0]['Lastname']
    assert dic[0]['LevelID_u']
    assert dic[0]['Password']
    assert dic[0]['Postcode']
    assert dic[0]['ProfilePic']
    assert dic[0]['UserID']

def test_get_faqs(client):
    rv = client.get('/faq/all')
    dic = json.loads(rv.data)
    assert dic[0]['Category']
    assert dic[0]['Detail']
    assert dic[0]['FAQID']
    assert dic[0]['FAQImage']
    assert dic[0]['Title']

def test_get_product(client):
    rv = client.get('/browse_product')
    dic = json.loads(rv.data)
    assert dic[0]['ItemID']
    assert dic[0]['ItemImage']
    assert dic[0]['LevelID_u']
    assert dic[0]['Name']
    assert dic[0]['Postcode']
    assert dic[0]['Price']

def test_get_single_product(client):
    rv = client.get('/view_product/1')
    dic = json.loads(rv.data)
    assert dic[0]['Date']
    assert dic[0]['Description']
    assert dic[0]['Display_name']
    assert dic[0]['ItemID']
    assert dic[0]['ItemImage']
    assert dic[0]['LevelID_u']
    assert dic[0]['Name']
    assert dic[0]['Postcode']
    assert dic[0]['Price']

def test_get_all_deal(client):
    rv = client.get('/get_deal_list/1')
    dic = json.loads(rv.data)
    assert dic[0]['Display_name']
    assert dic[0]['ItemDescription']
    assert dic[0]['ItemID']
    assert dic[0]['ItemImage']
    assert dic[0]['ItemName']

def test_get_one_deal(client):
    rv = client.get('/get_deal_info/1')
    dic = json.loads(rv.data)
    assert dic[0]['ChatID']
    assert dic[0]['Display_name']
    assert dic[0]['ItemDescription']
    assert dic[0]['ItemImage']
    assert dic[0]['ItemName']
    assert dic[0]['ProfilePic']
    assert dic[0]['UserID']

def test_get_one_chat(client):
    rv = client.get('/get_message_history/1')
    dic = json.loads(rv.data)
    assert dic[0]['ChatID_m']
    assert dic[0]['MessageID']
    assert dic[0]['SenderID']
    assert dic[0]['Text']
    assert dic[0]['Timestamp']
    assert dic[0]['IsRead'] != None

def test_get_last_message(client):
    rv = client.get('/get_latest_msg/1')
    dic = json.loads(rv.data)
    assert dic[0]['ChatID_m']
    assert dic[0]['MessageID']
    assert dic[0]['SenderID']
    assert dic[0]['Text']
    assert dic[0]['Timestamp']

def test_post_feedback(client):
    fileContent = {"timestamp":time.time()
    , "vote_status":1, "userID":1, "FAQID":[1]}
    rv = client.post('/faqfeedback', data = json.dumps(fileContent), content_type='application/json')
    dic = json.loads(rv.data)
    assert dic
    # assert dic['title']

def test_post_message(client):
    fileContent2 = {
    "chatID": 1,
    "senderID": 1,
    "message": "blabla from test",
    "timestamp": 1244567890
}
    rv = client.post('/send_message', data = json.dumps(fileContent2), content_type='application/json')
    # dic = json.loads(rv.data)
    # assert dic
    # assert dic['title']

# def login(client, username, password):
#     return client.post('/login', data=dict(
#         username=username,
#         password=password
#     ), follow_redirects=True)
#
#
# def logout(client):
#     return client.get('/logout', follow_redirects=True)
#
#
# def test_empty_db(client):
#     """Start with a blank database."""
#     rv = client.get('/')
#     assert b'No entries here so far' in rv.data
#
#
# def test_login_logout(client):
#     """Make sure login and logout works"""
#     rv = login(client, KaideeV.app.config['USERNAME'],
#                KaideeV.app.config['PASSWORD'])
#     assert b'You were logged in' in rv.data
#     rv = logout(client)
#     assert b'You were logged out' in rv.data
#     rv = login(client, KaideeV.app.config['USERNAME'] + 'x',
#                KaideeV.app.config['PASSWORD'])
#     assert b'Invalid username' in rv.data
#     rv = login(client, KaideeV.app.config['USERNAME'],
#                KaideeV.app.config['PASSWORD'] + 'x')
#     assert b'Invalid password' in rv.data
#
#
# def test_messages(client):
#     """Test that messages work"""
#     login(client, KaideeV.app.config['USERNAME'],
#           KaideeV.app.config['PASSWORD'])
#     rv = client.post('/add', data=dict(
#         title='<Hello>',
#         text='<strong>HTML</strong> allowed here'
#     ), follow_redirects=True)
#     assert b'No entries here so far' not in rv.data
#     assert b'&lt;Hello&gt;' in rv.data
#     assert b'<strong>HTML</strong> allowed here' in rv.data
