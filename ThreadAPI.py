__author__ = 'eugene'
from flask import Blueprint
from helperFuncs import *


thread_api = Blueprint('thread_api', __name__)


#------------------------------------------

#
#           /db/api/thread/close/
#           {"thread": 1}

@thread_api.route('/close/', methods=['POST'])
@connect_to_DB('threadClose')
def threadClose(cnx):

    cursor = cnx.cursor()
    inData = request.get_json(force=True)
    threadId = inData['thread']

    ThreadQueries.setClosed(cursor, threadId, 'True')
    cnx.commit()
    return jsonify({'code': Codes.OK, 'response': threadId})



#
#     db/api/thread/create/
# {"forum": "forum1", "title": "Thread With Sufficiently Large Title", "isClosed": true, "user": "example3@mail.ru", "date": "2014-01-01 00:00:01", "message": "hey hey hey hey!", "slug": "Threadwithsufficientlylargetitle", "isDeleted": true}
#
@thread_api.route('/create/', methods=['POST'])
@connect_to_DB('threadCreate')
def threadCreate(cnx):

    cursor = cnx.cursor()
    inData = request.get_json(force=True)

    forum = inData['forum']
    title = inData['title']
    isClosed = inData['isClosed']
    user = inData['user']
    date = inData['date']
    message = inData['message']
    slug = inData['slug']

    isDeleted = getValueOrFalse(inData, 'isDeleted')

    requiredParams = {'title': title, 'isClosed': isClosed, 'user': user, 'date': date,
                      'message': message, 'slug': slug, 'forum': forum, 'isDeleted': isDeleted}
    ThreadQueries.create(cursor, requiredParams)
    threadID = cursor.lastrowid
    cnx.commit()
    response = {"date": date, "forum": forum, "id": threadID, "isClosed": isClosed, "isDeleted": isDeleted,
                "message": message, "slug": slug, "title": title, "user": user}
    return jsonify({'code': Codes.OK, 'response': response})


#
#           /db/api/thread/details/?thread=1
#
@thread_api.route('/details/', methods=['GET'])
@connect_to_DB('threadDetails')
def threadDetails(cnx):

    cursor = cnx.cursor()
    related = getListOrEmpty(request.args, 'related')
    threadID = request.args.get('thread')
    if threadID is None:
        raise RequiredMissing("Thread required")

    thread = ThreadQueries.fetchById(cursor, threadID)
    response = completeThread(thread)

    if 'user' in related:
        response.update({'user': completeUser(UserQueries.fetchByEmail(cursor, response['user']))})
        related.remove('user')
    if 'forum' in related:
        response.update({'forum': completeForum(ForumQueries.fetchBySlug(cursor, response['forum']))})
        related.remove('forum')
    if 'thread' in related:
        return jsonify({'code': Codes.INCORRECT_DB_QUERY, 'response': "bad query"})
    return jsonify({'code': Codes.OK, 'response': response})


#
#       /db/api/thread/list/?since=2000-01-01+00%3A00%3A00&order=desc&forum=forumwithsufficientlylargename
#

@thread_api.route('/list/', methods=['GET'])
@connect_to_DB('threadList')
def threadList(cnx):

    cursor = cnx.cursor()
    since = request.args.get('since')
    limit = request.args.get('limit')
    order = request.args.get('order')

    short_name = request.args.get('forum')
    user = request.args.get('user')

    if(short_name is None) and (user is None):
        raise RequiredMissing('forum name or thread')
    if user is not None:
        threads = ThreadQueries.fetchUserThreads(cursor, user, since, limit, order)
    else:
        threads = ThreadQueries.fetchForumThreads(cursor, short_name, since, limit, order)
    response = []
    for thread in threads:
        response.append(completeThread(thread))
    return jsonify({'code': Codes.OK, 'response': response})


#
#       /db/api/thread/listPosts/?since=2000-01-02+00%3A00%3A00&limit=2&order=asc&thread=1
#
@thread_api.route('/listPosts/', methods=['GET'])
@connect_to_DB('threadListPosts')
def threadListPosts(cnx):

    cursor = cnx.cursor()
    since = request.args.get('since')
    limit = request.args.get('limit')
    order = request.args.get('order')
    sort = request.args.get('sort')
    threadID = request.args.get('thread')

    posts = PostQueries.fetchThreadPosts(cursor, threadID, since, limit, order, sort)
    response = []
    for post in posts:
        response.append(completePost(post))
    return jsonify({'code': Codes.OK, 'response': response})


#
#       /db/api/thread/open/
#       {"thread": 1}
@thread_api.route('/open/', methods=['POST'])
@connect_to_DB('threadOpen')
def threadOpen(cnx):

    cursor = cnx.cursor()
    inData = request.get_json(force=True)
    threadId = inData['thread']

    ThreadQueries.setClosed(cursor, threadId, False)
    cnx.commit()
    response = {"thread": threadId}
    return jsonify({'code': Codes.OK, 'response': response})

#
#       /db/api/thread/remove/
#       {"thread": 1}
@thread_api.route('/remove/', methods=['POST'])
@connect_to_DB('threadRemove')
def threadRemove(cnx):

    cursor = cnx.cursor()
    inData = request.get_json(force=True)
    threadId = inData['thread']

    ThreadQueries.setDeleted(cursor, threadId, True)
    cnx.commit()
    response = {"thread": threadId}
    return jsonify({'code': Codes.OK, 'response': response})


#
#       /db/api/thread/restore/
#       {"thread": 1}
@thread_api.route('/restore/', methods=['POST'])
@connect_to_DB('threadRestore')
def threadRestore(cnx):

    cursor = cnx.cursor()
    inData = request.get_json(force=True)
    threadId = inData['thread']

    ThreadQueries.setDeleted(cursor, threadId, False)
    cnx.commit()
    response = {"thread": threadId}
    return jsonify({'code': Codes.OK, 'response': response})


# TODO select before update
#           /db/api/thread/update/
#           {"message": "hey hey hey hey!", "slug": "newslug", "thread": 1}
@thread_api.route('/update/', methods=['POST'])
@connect_to_DB('threadUpdate')
def threadUpdate(cnx):

    cursor = cnx.cursor()
    inData = request.get_json(force=True)

    threadID = inData['thread']
    message = inData['message']
    slug = inData['slug']

    ThreadQueries.updMsgSlug(cursor, threadID, message, slug)
    cnx.commit()
    thread = ThreadQueries.fetchById(cursor, threadID)
    response = completeThread(thread)
    return jsonify({'code': Codes.OK, 'response': response})

#   TODO SELECT THREAD BEFORE UPDATE
#           /db/api/thread/vote/
#           {"vote": 1, "thread": 1}
@thread_api.route('/vote/', methods=['POST'])
@connect_to_DB('threadVote')
def threadVote(cnx):

    cursor = cnx.cursor()
    inData = request.get_json(force=True)
    threadId = inData['thread']
    vote = inData['vote']

    if vote == 1:
        liked = True
    elif vote == -1:
        liked = False
    else:
        raise RequiredMissing("vote")

    ThreadQueries.updVote(cursor, threadId, liked)
    cnx.commit()
    thread = ThreadQueries.fetchById(cursor, threadId)
    response = completeThread(thread)
    return jsonify({'code': Codes.OK, 'response': response})


#
#       /db/api/thread/subscribe/
#       {"user": "example@mail.ru", "thread": 4}
@thread_api.route('/subscribe/', methods=['POST'])
@connect_to_DB('threadSubscribe')
def threadSubscribe(cnx):

    cursor = cnx.cursor()
    inData = request.get_json(force=True)
    user = inData['user']
    threadID = inData['thread']
    ThreadQueries.subscribe(cursor, threadID, user)
    cnx.commit()
    response = {"thread": threadID, "user": user}

    return jsonify({'code': Codes.OK, 'response': response})

#
#       /db/api/thread/unsubscribe/
#       {"user": "example@mail.ru", "thread": 4}
@thread_api.route('/unsubscribe/', methods=['POST'])
@connect_to_DB('threadUnsubscribe')
def threadUnsubscribe(cnx):

    cursor = cnx.cursor()
    inData = request.get_json(force=True)
    user = inData['user']
    threadID = inData['thread']
    ThreadQueries.unsubscribe(cursor, threadID, user)
    cnx.commit()
    response = {"thread": threadID, "user": user}

    return jsonify({'code': Codes.OK, 'response': response})

#------------------------------------------
