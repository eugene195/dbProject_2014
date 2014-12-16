__author__ = 'eugene'
from flask import Blueprint
from helperFuncs import *


post_api = Blueprint('post_api', __name__)



# 



#------------------------------------------

#
#    db/api/post/create/
#    {"isApproved": true, "user": "example@mail.ru", "date": "2014-01-01 00:00:01", "message": "my message 1", "isSpam": false, "isHighlighted": true, "thread": 4, "forum": "forum2", "isDeleted": false, "isEdited": true}
#
# TODO WITHOUT POST SELECT
@post_api.route('/create/', methods=['POST'])
def createPost():
    try:
        cursor = cnx.cursor()
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

        PostQueries.create(cursor, requiredParams, optionalParams)
        cnx.commit()
        postID = cursor.lastrowid
        post = PostQueries.fetchById(cursor, postID)
        response = {
            "date": post[1], "forum": post[4], "id": post[0],
            "isApproved": post[6], "isDeleted": post[7], "isEdited": post[8],
            "isHighlighted": post[9], "isSpam": post[10],
            "message": post[11], "parent": post[13],
            "thread": post[15], "user": post[12]
        }
        fixDate(response)
        return jsonify({'code': Codes.OK, 'response': response})

    except DBNotFound as exc:
        return jsonify({'code': Codes.NOT_FOUND, 'response': exc.message})
    except (RequiredMissing, KeyError) as exc:
        return jsonify({'code': Codes.INVALID_QUERY, 'response': exc.message})
    except (OperationalError, IntegrityError) as exc:
        return jsonify({'code': Codes.INCORRECT_DB_QUERY, 'response': exc.msg})
    except Exception as exc:
        return jsonify({'code': Codes.UNKNOWN_ERROR, 'response': exc.message})

#
#        db/api/post/details/?post=3
#

@post_api.route('/details/', methods=['GET'])
def postDetails():
    try:
        cursor = cnx.cursor()
        related = getListOrEmpty(request.args, 'related')
        postID = request.args.get('post')
        postID = int(postID)
        post = PostQueries.fetchById(cursor, postID)
        response = completePost(post)
        if 'user' in related:
            response.update({'user': completeUser(UserQueries.fetchByEmail(cursor, response['user']))})
        if 'thread' in related:
            response.update({'thread': completeThread(ThreadQueries.fetchById(cursor, response['thread']))})
        if 'forum' in related:
            response.update({'forum': completeForum(ForumQueries.fetchBySlug(cursor, response['forum']))})
        return jsonify({'code': Codes.OK, 'response': response})
    except DBNotFound as exc:
        return jsonify({'code': Codes.NOT_FOUND, 'response': exc.message})
    except (RequiredMissing, KeyError) as exc:
        return jsonify({'code': Codes.INVALID_QUERY, 'response': exc.message})
    except (IntegrityError, OperationalError) as exc:
        return jsonify({'code': Codes.INCORRECT_DB_QUERY, 'response': exc.msg})
    except Exception as exc:
        return jsonify({'code': Codes.UNKNOWN_ERROR, 'response': exc.message})

#
#                   db/api/post/list/?since=2000-01-01+00%3A00%3A00&order=desc&forum=forum1
#

@post_api.route('/list/', methods=['GET'])
def postList():
    try:
        cursor = cnx.cursor()
        since = request.args.get('since')
        limit = request.args.get('limit')
        order = request.args.get('order')
        sort = request.args.get('sort')

        short_name = request.args.get('forum')
        thread = request.args.get('thread')

        if(short_name is None) and (thread is None):
            raise RequiredMissing('forum name or thread')
        if thread is not None:
            posts = PostQueries.fetchThreadPosts(cursor, thread, since, limit, order, sort)
        else:
            posts = PostQueries.fetchForumPosts(cursor, short_name, since, limit, order, sort)
        response = []
        for post in posts:
            response.append(completePost(post))
        return jsonify({'code': Codes.OK, 'response': response})
    except DBNotFound as exc:
        return jsonify({'code': Codes.NOT_FOUND, 'response': exc.message})
    except (RequiredMissing, KeyError) as exc:
        return jsonify({'code': Codes.INVALID_QUERY, 'response': exc.message})
    except (IntegrityError, OperationalError) as exc:
        return jsonify({'code': Codes.INCORRECT_DB_QUERY, 'response': exc.msg})
    except Exception as exc:
        return jsonify({'code': Codes.UNKNOWN_ERROR, 'response': exc.message})

#   TODO SINGLE UPDATE
#                        db/api/post/remove/
#       {"post": 3}

@post_api.route('/remove/', methods=['POST'])
def postRemove():
    try:
        cursor = cnx.cursor()
        inData = request.get_json(force=True)
        postId = inData['post']
        post = PostQueries.fetchById(cursor, postId)
        PostQueries.setDeleted(cursor, postId, True)
        cnx.commit()
        PostQueries.threadUpdatePostCount(cursor, post[15], ' - 1')
        cnx.commit()
        response = {'post': postId}
        return jsonify({'code': Codes.OK, 'response': response})
    except DBNotFound as exc:
        return jsonify({'code': Codes.NOT_FOUND, 'response': exc.message})
    except (RequiredMissing, KeyError) as exc:
        return jsonify({'code': Codes.INVALID_QUERY, 'response': exc.message})
    except (IntegrityError, OperationalError) as exc:
        return jsonify({'code': Codes.INCORRECT_DB_QUERY, 'response': exc.msg})
    except Exception as exc:
        return jsonify({'code': Codes.UNKNOWN_ERROR, 'response': exc.message})


#
#              db/api/post/restore/
#               {"post": 3}

@post_api.route('/restore/', methods=['POST'])
def postRestore():
    try:
        cursor = cnx.cursor()
        inData = request.get_json(force=True)
        postId = inData['post']
        post = PostQueries.fetchById(cursor, postId)
        PostQueries.setDeleted(cursor, postId, False)
        cnx.commit()
        PostQueries.threadUpdatePostCount(cursor, post[15], ' + 1')
        cnx.commit()
        response = {'post': postId}
        return jsonify({'code': Codes.OK, 'response': response})
    except DBNotFound as exc:
        return jsonify({'code': Codes.NOT_FOUND, 'response': exc.message})
    except (RequiredMissing, KeyError) as exc:
        return jsonify({'code': Codes.INVALID_QUERY, 'response': exc.message})
    except (IntegrityError, OperationalError) as exc:
        return jsonify({'code': Codes.INCORRECT_DB_QUERY, 'response': exc.msg})
    except Exception as exc:
        return jsonify({'code': Codes.UNKNOWN_ERROR, 'response': exc.message})

#   TODO SELECT BEFORE UPDATE
#           db/api/post/update/
#           {"post": 3, "message": "my message 1"}

@post_api.route('/update/', methods=['POST'])
def postUpdate():
    try:
        cursor = cnx.cursor()
        inData = request.get_json(force=True)
        postId = inData['post']
        message = inData['message']

        PostQueries.updMessage(cursor, postId, message)
        cnx.commit()
        post = PostQueries.fetchById(cursor, postId)
        response = completePost(post)
        return jsonify({'code': Codes.OK, 'response': response})
    except DBNotFound as exc:
        return jsonify({'code': Codes.NOT_FOUND, 'response': exc.message})
    except (RequiredMissing, KeyError) as exc:
        return jsonify({'code': Codes.INVALID_QUERY, 'response': exc.message})
    except (IntegrityError, OperationalError) as exc:
        return jsonify({'code': Codes.INCORRECT_DB_QUERY, 'response': exc.msg})
    except Exception as exc:
        return jsonify({'code': Codes.UNKNOWN_ERROR, 'response': exc.message})

# TODO SELECT BEFORE UPDATE
#       /db/api/post/vote/
#       {"vote": -1, "post": 5}

@post_api.route('/vote/', methods=['POST'])
def postVote():
    try:
        cursor = cnx.cursor()
        inData = request.get_json(force=True)

        postId = inData['post']
        vote = inData['vote']
        if (vote == 1):
            liked = True
        elif (vote == -1):
            liked = False
        else:
            raise BadFormat("vote")
        PostQueries.updVote(cursor, postId, liked)
        cnx.commit()
        post = PostQueries.fetchById(cursor, postId)
        response = completePost(post)
        return jsonify({'code': Codes.OK, 'response': response})
    except DBNotFound as exc:
        return jsonify({'code': Codes.NOT_FOUND, 'response': exc.message})
    except (RequiredMissing, KeyError, BadFormat) as exc:
        return jsonify({'code': Codes.INVALID_QUERY, 'response': exc.message})
    except (IntegrityError, OperationalError) as exc:
        return jsonify({'code': Codes.INCORRECT_DB_QUERY, 'response': exc.msg})
    except Exception as exc:
        return jsonify({'code': Codes.UNKNOWN_ERROR, 'response': exc.message})
