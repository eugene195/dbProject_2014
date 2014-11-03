__author__ = 'eugene'
from flask import request, jsonify, render_template

from sqlhelper import UserQueries, ForumQueries, PostQueries, ThreadQueries, DBNotFound, RequiredMissing, BadFormat, UtilQueries
import mysql.connector
from mysql.connector import errorcode
from mysql.connector.errors import IntegrityError, OperationalError



# Core settings
# ----------------------------------------------
PREFIX = "/db/api"

cnx = mysql.connector.connect(user='root', password='root',
                          host='127.0.0.1',
                          database='dbProject')


# Return default value if object is not valid
# ----------------------------------------------
def getNoneIfZero(obj):
    if obj == 0:
        return None
    return obj

def getValueOrFalse(inData, str):
    try:
        variable = inData[str]
    except KeyError:
        variable = False
    return variable

def getValueOrZero(inData, str):
    try:
        variable = inData[str]
    except KeyError:
        variable = 0
    return variable

def getValueOrNullStr(inData, str):
    try:
        variable = inData[str]
    except KeyError:
        variable = 'NULL'
    return variable

def getValueOrEmptyStr(inData, str):
    try:
        variable = inData[str]
    except KeyError:
        variable = ''
    return variable

def getListOrEmpty(inData, name):
    try:
        variable = inData.getlist(name)
    except Exception:
        variable = []
    return variable

def returnFalseIfZero(val):
    if val == 0:
        return False
    else:
        return True

# ----------------------------------------------
# Python dictionary from list
# ----------------------------------------------

def fixDate(object):
    object['date'] = object['date'].strftime("%Y-%m-%d %H:%M:%S")

def completePost(post):
    complete = {
                "date": post[1], "dislikes": post[3], "forum": post[4], "id": post[0],
                "isApproved": bool(post[6]), "isDeleted": bool(post[7]), "isEdited": bool(post[8]),
                "isHighlighted": bool(post[9]), "isSpam": bool(post[10]), "likes": post[2],
                "message": post[11], "parent": getNoneIfZero(post[13]), "points": post[14],
                "thread": post[15], "user": post[12]
                }
    fixDate(complete)
    return complete

def completeForum(forum):
    complete = {'id': forum[0], 'name': forum[1], 'short_name': forum[2], 'user': forum[3]}
    return complete

def completeThread(thread):
    complete = {
                "date": thread[1], "dislikes": thread[2], "forum": thread[12],
                "id": thread[0], "isClosed": bool(thread[4]), "isDeleted": bool(thread[5]),
                "likes": thread[3], "message": thread[11], "points": thread[6],
                "posts": thread[7], "slug": thread[8], "title": thread[9], "user": thread[10]
                }
    fixDate(complete)
    return complete

def completeUser(user):
    cursor = cnx.cursor()
    complete = {
                "about": user[0], "email": user[1],
                "followers": getList(UserQueries.getFollowers(cursor, user[1])),
                "following": getList(UserQueries.getFollowee(cursor, user[1])),
                "id": user[2], "isAnonymous": bool(user[3]), "name": user[4],
                "subscriptions": getList(UserQueries.getSubscriptions(cursor, user[1])),
                "username": user[5]
                }


    if (complete['isAnonymous'] == True):
        complete['username'] = None
        complete['name'] = None
        complete['about'] = None
    return complete
# ----------------------------------------------
# Create normal list from raw SSQL return
# ----------------------------------------------

def getList(rawOut):
    mylist = []
    for entry in rawOut:
        mylist.append(entry[0])
    return mylist

# ----------------------------------------------
# Error codes
# ----------------------------------------------
class Codes:
    OK = 0
    NOT_FOUND = 1
    INVALID_QUERY = 2
    INCORRECT_DB_QUERY = 3
    UNKNOWN_ERROR = 4
    USER_EXISTS = 5