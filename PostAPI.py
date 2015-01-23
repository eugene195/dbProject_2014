__author__ = 'eugene'
from flask import Blueprint
from helperFuncs import *


post_api = Blueprint('post_api', __name__)


#------------------------------------------

#
#    db/api/post/create/
#    {"isApproved": true, "user": "example@mail.ru", "date": "2014-01-01 00:00:01", "message": "my message 1", "isSpam": false, "isHighlighted": true, "thread": 4, "forum": "forum2", "isDeleted": false, "isEdited": true}
#
@post_api.route('/create/', methods=['POST'])
@connect_to_DB('createPost')
def createPost(cnx, curs):

    
    inData = request.get_json(force=True)

    parent = getValueOrZero(inData, 'parent')
    isApproved = getValueOrFalse(inData, 'isApproved')
    isHighlighted = getValueOrFalse(inData, 'isHighlighted')
    isEdited = getValueOrFalse(inData, 'isEdited')
    isSpam = getValueOrFalse(inData, 'isSpam')
    isDeleted = getValueOrFalse(inData, 'isDeleted')

    date = inData['date']
    threadID = inData['thread']
    message = inData['message']
    user = inData['user']
    forum = inData['forum']
    requiredParams = {'date': date, 'thread': threadID, 'message': message, 'user': user, 'forum': forum}
    optionalParams = {'isApproved': isApproved, 'isHighlighted': isHighlighted, 'isEdited': isEdited,
                    'isSpam': isSpam, 'isDeleted': isDeleted, 'parent': parent}

    PostQueries.create(curs, requiredParams, optionalParams)
    cnx.commit()
    postID = curs.lastrowid
    response = {
        "date": date, "forum": forum, "id":postID,
        "isApproved": isApproved, "isDeleted": isDeleted, "isEdited": isEdited,
        "isHighlighted": isHighlighted, "isSpam": isSpam,
        "message": message, "parent": parent,
        "thread": threadID, "user": user
    }
    return jsonify({'code': Codes.OK, 'response': response})


#
#        db/api/post/details/?post=3
#

@post_api.route('/details/', methods=['GET'])
@connect_to_DB('postDetails')
def postDetails(cnx, curs):

    
    related = getListOrEmpty(request.args, 'related')
    postID = request.args.get('post')
    postID = int(postID)
    post = PostQueries.fetchById(curs, postID)
    response = completePost(post)
    if 'user' in related:
        response.update({'user': completeUser(UserQueries.fetchByEmail(curs, response['user']), cnx)})
    if 'thread' in related:
        response.update({'thread': completeThread(ThreadQueries.fetchById(curs, response['thread']))})
    if 'forum' in related:
        response.update({'forum': completeForum(ForumQueries.fetchBySlug(curs, response['forum']))})
    return jsonify({'code': Codes.OK, 'response': response})


#
#                   db/api/post/list/?since=2000-01-01+00%3A00%3A00&order=desc&forum=forum1
#

@post_api.route('/list/', methods=['GET'])
@connect_to_DB('postList')
def postList(cnx, curs):

    
    since = request.args.get('since')
    limit = request.args.get('limit')
    order = request.args.get('order')
    sort = request.args.get('sort')

    short_name = request.args.get('forum')
    thread = request.args.get('thread')

    if(short_name is None) and (thread is None):
        raise RequiredMissing('forum name or thread')
    if thread is not None:
        posts = PostQueries.fetchThreadPosts(curs, thread, since, limit, order, sort)
    else:
        posts = PostQueries.fetchForumPosts(curs, short_name, since, limit, order, sort)
    response = []
    for post in posts:
        response.append(completePost(post))
    return jsonify({'code': Codes.OK, 'response': response})


#   TODO SINGLE UPDATE
#                        db/api/post/remove/
#       {"post": 3}

@post_api.route('/remove/', methods=['POST'])
@connect_to_DB('postRemove')
def postRemove(cnx, curs):

    
    inData = request.get_json(force=True)
    postId = inData['post']
    post = PostQueries.fetchById(curs, postId)
    PostQueries.setDeleted(curs, postId, True)
    cnx.commit()
    PostQueries.threadUpdatePostCount(curs, post[15], ' - 1')
    cnx.commit()
    response = {'post': postId}
    return jsonify({'code': Codes.OK, 'response': response})



#
#              db/api/post/restore/
#               {"post": 3}

@post_api.route('/restore/', methods=['POST'])
@connect_to_DB('postRestore')
def postRestore(cnx, curs):

    
    inData = request.get_json(force=True)
    postId = inData['post']
    post = PostQueries.fetchById(curs, postId)
    PostQueries.setDeleted(curs, postId, False)
    cnx.commit()
    PostQueries.threadUpdatePostCount(curs, post[15], ' + 1')
    cnx.commit()
    response = {'post': postId}
    return jsonify({'code': Codes.OK, 'response': response})



#           db/api/post/update/
#           {"post": 3, "message": "my message 1"}

@post_api.route('/update/', methods=['POST'])
@connect_to_DB('postUpdate')
def postUpdate(cnx, curs):

    
    inData = request.get_json(force=True)
    postId = inData['post']
    message = inData['message']

    PostQueries.updMessage(curs, postId, message)
    cnx.commit()
    post = PostQueries.fetchById(curs, postId)
    response = completePost(post)
    return jsonify({'code': Codes.OK, 'response': response})



#       /db/api/post/vote/
#       {"vote": -1, "post": 5}

@post_api.route('/vote/', methods=['POST'])
@connect_to_DB('postVote')
def postVote(cnx, curs):

    
    inData = request.get_json(force=True)

    postId = inData['post']
    vote = inData['vote']
    if (vote == 1):
        liked = True
    elif (vote == -1):
        liked = False
    else:
        raise BadFormat("vote")
    PostQueries.updVote(curs, postId, liked)
    cnx.commit()
    post = PostQueries.fetchById(curs, postId)
    response = completePost(post)
    return jsonify({'code': Codes.OK, 'response': response})

