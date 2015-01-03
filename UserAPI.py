__author__ = 'eugene'

from flask import Blueprint
from helperFuncs import *


user_api = Blueprint('user_api', __name__)


#
#           db/api/user/create/
#  {"username": "user1", "about": "hello im user1", "isAnonymous": false, "name": "John", "email": "example@mail.ru"}
#
@user_api.route('/create/', methods=['POST'])
@connect_to_DB('userCreate')
def userCreate(cnx):

    cursor = cnx.cursor()
    inData = request.get_json(force=True)

    about = inData['about']
    name = inData['name']
    username = inData['username']
    email = inData['email']
    isAnonymous = getValueOrFalse(inData, 'isAnonymous')

    requiredParams = {'about': about, 'name': name, 'username': username, 'email': email, 'isAnonymous': isAnonymous}

    UserQueries.create(cursor, requiredParams)
    cnx.commit()
    userId = cursor.lastrowid
    response = {"about": about, "email": email, "id": userId,
                "isAnonymous": bool(isAnonymous), "name": name, "username": username}
    return jsonify({'code': Codes.OK, 'response': response})



#
#           /db/api/user/details/?user=example%40mail.ru
#
@user_api.route('/details/', methods=['GET'])
@connect_to_DB('userDetails')
def userDetails(cnx):
    cursor = cnx.cursor()
    email = request.args.get('user')
    user = UserQueries.fetchByEmail(cursor, email)
    response = completeUser(user, cnx)
    return jsonify({'code': Codes.OK, 'response': response})


# TODO SELECT BEFORE UPDATE
#       /db/api/user/follow/
#        {"follower": "example@mail.ru", "followee": "example3@mail.ru"}
#
@user_api.route('/follow/', methods=['POST'])
@connect_to_DB('userFollow')
def userFollow(cnx):

    cursor = cnx.cursor()
    inData = request.get_json(force=True)

    followee = inData['followee']
    follower = inData['follower']

    UserQueries.follow(cursor, followee, follower)
    cnx.commit()

    user = UserQueries.fetchByEmail(cursor, follower)
    response= completeUser(user, cnx)

    return jsonify({'code': Codes.OK, 'response': response})


#
#       /db/api/user/listFollowers/?user=example%40mail.ru&order=asc
#
@user_api.route('/listFollowers/', methods=['GET'])
@connect_to_DB('userListFollowers')
def userListFollowers(cnx):

    cursor = cnx.cursor()
    since_id = request.args.get('since_id')
    limit = request.args.get('limit')
    order = request.args.get('order')

    user = request.args.get('user')
    followers = UserQueries.getUsersFollowers(cursor, user, since_id, limit, order)
    response = []
    for follower in followers:
        person = {
            'about': follower[3], 'email': follower[4], 'id': follower[5],
            'name': follower[7], 'username': follower[8], 'isAnonymous': bool(follower[6]),
            "followers": getList(UserQueries.getFollowers(cursor, follower[4])),
            "following": getList(UserQueries.getFollowee(cursor, follower[4])),
            "subscriptions": getList(UserQueries.getSubscriptions(cursor, follower[4]))
        }
        response.append(person)

    return jsonify({'code': Codes.OK, 'response': response})

#
#       /db/api/user/listFollowee/?user=example%40mail.ru&order=asc
#
@user_api.route('/listFollowing/', methods=['GET'])
@connect_to_DB('userListFollowee')
def userListFollowee(cnx):

    cursor = cnx.cursor()
    since_id = request.args.get('since_id')
    limit = request.args.get('limit')
    order = request.args.get('order')

    user = request.args.get('user')
    followee = UserQueries.getUsersFollowee(cursor, user, since_id, limit, order)
    response = []
    for human in followee:
        person = {
            'about': human[3], 'email': human[4], 'id': human[5],
            'name': human[7], 'username': human[8], 'isAnonymous': bool(human[6]),
            "followers": getList(UserQueries.getFollowers(cursor, human[4])),
            "following": getList(UserQueries.getFollowee(cursor, human[4])),
            "subscriptions": getList(UserQueries.getSubscriptions(cursor, human[4]))
        }
        response.append(person)

    return jsonify({'code': Codes.OK, 'response': response})

#
#       /db/api/user/listPosts/?since=2000-01-02+00%3A00%3A00&limit=2&user=example%40mail.ru&order=asc
#
@user_api.route('/listPosts/', methods=['GET'])
@connect_to_DB('userListPosts')
def userListPosts(cnx):

    cursor = cnx.cursor()
    since = request.args.get('since')
    limit = request.args.get('limit')
    order = request.args.get('order')

    user = request.args.get('user')
    posts = PostQueries.fetchUserPosts(cursor, user, since, limit, order)
    response = []
    for post in posts:
        complete = completePost(post)
        response.append(complete)

    return jsonify({'code': Codes.OK, 'response': response})

# TODO SELECT BEFORE UPDATE
#       /db/api/user/unfollow/
#       {"follower": "example@mail.ru", "followee": "example3@mail.ru"}
@user_api.route('/unfollow/', methods=['POST'])
@connect_to_DB('userUnfollow')
def userUnfollow(cnx):

    cursor = cnx.cursor()
    inData = request.get_json(force=True)
    followee = inData['followee']
    follower = inData['follower']

    UserQueries.unfollow(cursor, followee, follower)
    cnx.commit()
    user = UserQueries.fetchByEmail(cursor, follower)
    response = completeUser(user, cnx)

    return jsonify({'code': Codes.OK, 'response': response})

## TODO SELECT BEFORE UPDATE
#       /db/api/user/updateProfile/
#       {"about": "Wowowowow!!!", "user": "example@mail.ru", "name": "NewName2"}
@user_api.route('/updateProfile/', methods=['POST'])
@connect_to_DB('userUpdate')
def userUpdate(cnx):

    cursor = cnx.cursor()
    inData = request.get_json(force=True)

    about = inData['about']
    email = inData['user']
    name = inData['name']

    UserQueries.updateProfile(cursor, email, about, name)
    cnx.commit()
    user = UserQueries.fetchByEmail(cursor, email)
    response = completeUser(user, cnx)
    return jsonify({'code': Codes.OK, 'response': response})

