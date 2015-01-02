__author__ = 'eugene'
from flask import Blueprint
from helperFuncs import *


forum_api = Blueprint('forum_api', __name__)

#
#  Requesting http://some.host.ru/db/api/forum/create/ with
# {"name": "Forum With Sufficiently Large Name", "short_name": "forumwithsufficientlylargename", "user": "richard.nixon@example.com"}:
#
@forum_api.route('/create/', methods=['POST'])
@connect_to_DB('createForum')
def createForum(cnx):

    cursor = cnx.cursor()
    inData = request.get_json(force=True)
    name = inData['name']
    short_name = inData['short_name']
    email = inData['user']

    ForumQueries.create(cursor, name, short_name, email)
    cnx.commit()
    forunID = cursor.lastrowid

    response = {'id': forunID, 'name': name, 'short_name': short_name, 'user': email}
    return jsonify({'code': Codes.OK, 'response': response})



#
#           /db/api/forum/details/?related=user&forum=forum3:
#
@forum_api.route('/details/', methods=['GET'])
@connect_to_DB('forumDetails')
def forumDetails(cnx):

    cursor = cnx.cursor()
    related = getListOrEmpty(request.args, 'related')
    short_name = request.args.get('forum')

    forum = ForumQueries.fetchBySlug(cursor, short_name)
    response = completeForum(forum)
    if 'user' in related:
        user = UserQueries.fetchByEmail(cursor, forum[3])
        userD = {'user': completeUser(user)}
        response.update(userD)

    return jsonify({'code': Codes.OK, 'response': response})


#
#       /db/api/forum/listPosts/?related=thread&related=forum&since=2000-01-01+00%3A00%3A00&order=desc&forum=forumwithsufficientlylargename
#

@forum_api.route('/listPosts/', methods=['GET'])
@connect_to_DB('forumListPosts')
def forumListPosts(cnx):

    cursor = cnx.cursor()
    since = request.args.get('since')
    limit = request.args.get('limit')
    sort = request.args.get('sort')
    order = request.args.get('order')
    related = getListOrEmpty(request.args, 'related')

    short_name = request.args.get('forum')

    posts = PostQueries.fetchForumPosts(cursor, short_name, since, limit, order, sort)
    response = []
    for post in posts:
        post = completePost(post)
        if 'user' in related:
            post.update({'user': completeUser(UserQueries.fetchByEmail(cursor, post['user']))})
        if 'forum' in related:
            forum = ForumQueries.fetchBySlug(cursor, short_name)
            post.update({'forum': completeForum(forum)})
        if 'thread' in related:
            post.update({'thread': completeThread(ThreadQueries.fetchById(cursor, post['thread']))})
        response.append(post)

    return jsonify({'code': Codes.OK, 'response': response})

#
#           /db/api/forum/listThreads/?related=forum&since=2013-12-31+00%3A00%3A00&order=desc&forum=forumwithsufficientlylargename
#
@forum_api.route('/listThreads/', methods=['GET'])
@connect_to_DB('forumListThreads')
def forumListThreads(cnx):

    cursor = cnx.cursor()
    since = request.args.get('since')
    limit = request.args.get('limit')
    order = request.args.get('order')
    related = getListOrEmpty(request.args, 'related')

    short_name = request.args.get('forum')
    threads = ThreadQueries.fetchForumThreads(cursor, short_name, since, limit, order)

    response = []
    for thread in threads:
        thread = completeThread(thread)
        if 'user' in related:
            thread.update({'user': completeUser(UserQueries.fetchByEmail(cursor, thread['user']))})

        if 'forum' in related:
            forum = ForumQueries.fetchBySlug(cursor, short_name)
            thread.update({'forum': completeForum(forum)})
        response.append(thread)

    return jsonify({'code': Codes.OK, 'response': response})

#
#       /db/api/forum/listUsers/?order=desc&forum=forumwithsufficientlylargename
#

@forum_api.route('/listUsers/', methods=['GET'])
@connect_to_DB('forumListUsers')
def forumListUsers(cnx):

    cursor = cnx.cursor()
    since_id = request.args.get('since_id')
    limit = request.args.get('limit')
    order = request.args.get('order')

    short_name = request.args.get('forum')
    users = UserQueries.fetchForumUsers(cursor, short_name, since_id, limit, order)
    response = []
    noneUsers = []
    for user in users:
        complete = completeUser(user)
        if complete['username'] == 'None' or complete['name'] == 'None' or complete['isAnonymous']:
            noneUsers.append(complete)
        else:
            response.append(complete)
    for user in noneUsers:
        response.append(user)

    return jsonify({'code': Codes.OK, 'response': response})
