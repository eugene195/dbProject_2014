__author__ = 'eugene'
from flask import Blueprint
from helperFuncs import *


forum_api = Blueprint('forum_api', __name__)

#
#  Requesting http://some.host.ru/db/api/forum/create/ with
# {"name": "Forum With Sufficiently Large Name", "short_name": "forumwithsufficientlylargename", "user": "richard.nixon@example.com"}:
#
@forum_api.route('/create/', methods=['POST'])
def createForum():
    try:
        cursor = cnx.cursor()
        inData = request.get_json(force=True)
        name = inData['name']
        short_name = inData['short_name']
        email = inData['user']

        try:
            ForumQueries.create(cursor, name, short_name, email)
            cnx.commit()
        except IntegrityError as exc:
            pass
        forum = ForumQueries.fetchBySlug(cursor, short_name)

        response = {'id': forum[0], 'name': name, 'short_name': short_name, 'user': email}
        return jsonify({'code': Codes.OK, 'response': response})
    except DBNotFound as exc:
        return jsonify({'code': Codes.NOT_FOUND, 'response': exc.message})
    except (RequiredMissing, KeyError) as exc:
        return jsonify({'code': Codes.INVALID_QUERY, 'response': exc.message})
    except (OperationalError) as exc:
        return jsonify({'code': Codes.INCORRECT_DB_QUERY, 'response': exc.msg})
    except Exception as exc:
        return jsonify({'code': Codes.UNKNOWN_ERROR, 'response': exc.message})


#
#           /db/api/forum/details/?related=user&forum=forum3:
#
@forum_api.route('/details/', methods=['GET'])
def forumDetails():
    try:
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
    except DBNotFound as exc:
        return jsonify({'code': Codes.NOT_FOUND, 'response': exc.message})
    except (RequiredMissing, KeyError) as exc:
        return jsonify({'code': Codes.INVALID_QUERY, 'response': exc.message})
    except (IntegrityError, OperationalError) as exc:
        return jsonify({'code': Codes.INCORRECT_DB_QUERY, 'response': exc.msg})
    except Exception as exc:
        return jsonify({'code': Codes.UNKNOWN_ERROR, 'response': exc.message})

#
#       /db/api/forum/listPosts/?related=thread&related=forum&since=2000-01-01+00%3A00%3A00&order=desc&forum=forumwithsufficientlylargename
#

@forum_api.route('/listPosts/', methods=['GET'])
def forumListPosts():
    try:
        cursor = cnx.cursor()
        since = request.args.get('since')
        limit = request.args.get('limit')
        sort = request.args.get('sort')
        order = request.args.get('order')
        related = getListOrEmpty(request.args, 'related')

        short_name = request.args.get('forum')
        forum = ForumQueries.fetchBySlug(cursor, short_name)
        posts = PostQueries.fetchForumPosts(cursor, short_name, since, limit, order, sort)
        response = []
        for post in posts:
            post = completePost(post)
            if 'user' in related:
                post.update({'user': completeUser(UserQueries.fetchByEmail(cursor, post['user']))})
            if 'forum' in related:
                post.update({'forum': completeForum(forum)})
            if 'thread' in related:
                post.update({'thread': completeThread(ThreadQueries.fetchById(cursor, post['thread']))})
            response.append(post)

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
#           /db/api/forum/listThreads/?related=forum&since=2013-12-31+00%3A00%3A00&order=desc&forum=forumwithsufficientlylargename
#
@forum_api.route('/listThreads/', methods=['GET'])
def forumListThreads():
    try:
        cursor = cnx.cursor()
        since = request.args.get('since')
        limit = request.args.get('limit')
        order = request.args.get('order')
        related = getListOrEmpty(request.args, 'related')

        short_name = request.args.get('forum')
        forum = ForumQueries.fetchBySlug(cursor, short_name)
        threads = ThreadQueries.fetchForumThreads(cursor, short_name, since, limit, order)

        response = []
        for thread in threads:
            thread = completeThread(thread)
            if 'user' in related:
                thread.update({'user': completeUser(UserQueries.fetchByEmail(cursor, thread['user']))})

            if 'forum' in related:
                thread.update({'forum': completeForum(forum)})
            response.append(thread)

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
#       /db/api/forum/listUsers/?order=desc&forum=forumwithsufficientlylargename
#

@forum_api.route('/listUsers/', methods=['GET'])
def forumListUsers():
    try:
        cursor = cnx.cursor()
        since_id = request.args.get('since_id')
        limit = request.args.get('limit')
        order = request.args.get('order')

        short_name = request.args.get('forum')
        users = UserQueries.fetchForumUsers(cursor, short_name, since_id, limit, order)
        response = []
        for user in users:
            response.append(completeUser(user))

        return jsonify({'code': Codes.OK, 'response': response})
    except DBNotFound as exc:
        return jsonify({'code': Codes.NOT_FOUND, 'response': exc.message})
    except (RequiredMissing, KeyError) as exc:
        return jsonify({'code': Codes.INVALID_QUERY, 'response': exc.message})
    except (IntegrityError, OperationalError) as exc:
        return jsonify({'code': Codes.INCORRECT_DB_QUERY, 'response': exc.msg})
    except Exception as exc:
        return jsonify({'code': Codes.UNKNOWN_ERROR, 'response': exc.message})
