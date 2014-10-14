__author__ = 'eugene'

from flask import Flask
from flask import request, jsonify, render_template

from sqlhelper import UserQueries, ForumQueries, PostQueries, ThreadQueries, DBNotFound, RequiredMissing, BadFormat

from mysql.connector.errors import IntegrityError
from mysql.connector.errors import OperationalError


import mysql.connector

from mysql.connector import errorcode


class Codes:
    OK = 0
    NOT_FOUND = 1
    INVALID_QUERY = 2
    INCORRECT_DB_QUERY = 3
    UNKNOWN_ERROR = 4
    USER_EXISTS = 5

cnx = mysql.connector.connect(user='root', password='root',
                          host='127.0.0.1',
                          database='dbProject')

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

def getValueOrNull(inData, str):
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

def completeUser(user):
    cursor = cnx.cursor()
    complete = {
                "about": user[0], "email": user[1],
                "followers": UserQueries.getUsersFollowers(cursor, user[1], None, None, None),
                "following": UserQueries.getUsersFollowee(cursor, user[1], None, None, None),
                "id": user[2], "isAnonymous": returnFalseIfZero(user[3]), "name": user[4],
                "subscriptions": UserQueries.getSubscriptions(cursor, user[1]),
                "username": user[5]
                }
    return complete

def completePost(post):
    cursor = cnx.cursor()
    complete = {
        "date": post[1], "dislikes": post[3], "forum": post[4], "id": post[0],
        "isApproved": post[5], "isDeleted": post[6], "isEdited": post[7], "isHighlighted": post[8], "isSpam": post[9],
        "likes": post[2], "message": post[10], "parent": post[12],
        "points": post[13], "thread": post[14], "user": post[11]
    }
    return complete

def completeForum(forum):
    complete = {'id': forum[0], 'name': forum[1], 'short_name': forum[2], 'user': forum[3]}
    return complete

def completeThread(thread):
    cursor = cnx.cursor()
    complete = {
        "date": thread[1], "dislikes": thread[2], "forum": thread[12], "id": thread[0], "isClosed": thread[4],
        "isDeleted": thread[5], "likes": thread[3], "message": thread[11], "points": thread[6], "posts": thread[7],
        "slug": thread[8], "title": thread[9], "user": thread[10]
    }
    return complete

app = Flask(__name__)

# TODO +
@app.route('/forum/create/', methods=['POST'])
def createForum():
    try:
        cursor = cnx.cursor()
        inData = request.get_json(force=True)
        name = inData['name']
        short_name = inData['short_name']
        email = inData['user']

        # Does User with this email exist?
        user = UserQueries.fetchByEmail(cursor, email)

        ForumQueries.create(cursor, name, short_name, email)
        cnx.commit()
        forum = ForumQueries.fetchBySlug(cursor, short_name)

        response = {'id': forum[0], 'name': name, 'short_name': short_name, 'user': email}
        return jsonify({'code': Codes.OK, 'response': response})
    except DBNotFound as exc:
        return jsonify({'code': Codes.NOT_FOUND, 'response': exc.message})
    except (RequiredMissing, KeyError) as exc:
        return jsonify({'code': Codes.INVALID_QUERY, 'response': exc.message})
    except (IntegrityError, OperationalError) as exc:
        return jsonify({'code': Codes.INCORRECT_DB_QUERY, 'response': exc.msg})
    except Exception as exc:
        return jsonify({'code': Codes.UNKNOWN_ERROR, 'response': exc.message})


#TODO +, SQL ERRORS IN FOLLOWERS
@app.route('/forum/details/', methods=['GET'])
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

#TODO +, ADD SORT, LIMIT
@app.route('/forum/listPosts/', methods=['GET'])
def forumListPosts():
    try:
        cursor = cnx.cursor()
        # OPTIONAL
        since = request.args.get('since')
        limit = request.args.get('limit')
        # sort = request.args.get('sort')
        order = request.args.get('order')
        related = getListOrEmpty(request.args, 'related')

        short_name = request.args.get('forum')
        forum = ForumQueries.fetchBySlug(cursor, short_name)
        posts = PostQueries.fetchForumPosts(cursor, short_name, since, limit, order)

        for post in posts:
            completePost(post)
            if 'user' in related:
                post.update({'user': completeUser(UserQueries.fetchByEmail(cursor, post['user']))})
            if 'forum' in related:
                post.update({'forum': completeForum(forum)})
            if 'thread' in related:
                post.update({'thread': completeThread(ThreadQueries.fetchById(cursor, post['thread']))})

        return jsonify({'code': Codes.OK, 'response': posts})
    except DBNotFound as exc:
        return jsonify({'code': Codes.NOT_FOUND, 'response': exc.message})
    except (RequiredMissing, KeyError) as exc:
        return jsonify({'code': Codes.INVALID_QUERY, 'response': exc.message})
    except (IntegrityError, OperationalError) as exc:
        return jsonify({'code': Codes.INCORRECT_DB_QUERY, 'response': exc.msg})
    except Exception as exc:
        return jsonify({'code': Codes.UNKNOWN_ERROR, 'response': exc.message})

#TODO +, LIMIT, COMPLETE
@app.route('/forum/listThreads/', methods=['GET'])
def forumListThreads():
    try:
        cursor = cnx.cursor()
        # OPTIONAL
        since = request.args.get('since')
        limit = request.args.get('limit')
        order = request.args.get('order')
        related = getListOrEmpty(request.args, 'related')

        short_name = request.args.get('forum')
        forum = ForumQueries.fetchBySlug(cursor, short_name)
        threads = ThreadQueries.fetchForumThreads(cursor, short_name, since, limit, order)

        for thread in threads:
            if 'user' in related:
                thread.update({'user': completeUser(UserQueries.fetchByEmail(cursor, thread['user']))})

            if 'forum' in related:
                thread.update({'forum': completeForum(forum)})

        return jsonify({'code': Codes.OK, 'response': threads})
    except DBNotFound as exc:
        return jsonify({'code': Codes.NOT_FOUND, 'response': exc.message})
    except (RequiredMissing, KeyError) as exc:
        return jsonify({'code': Codes.INVALID_QUERY, 'response': exc.message})
    except (IntegrityError, OperationalError) as exc:
        return jsonify({'code': Codes.INCORRECT_DB_QUERY, 'response': exc.msg})
    except Exception as exc:
        return jsonify({'code': Codes.UNKNOWN_ERROR, 'response': exc.message})

# TODO +, CHECK COMPLETEUSER (WILL IT CHANGE THE RESPONSE)
@app.route('/forum/listUsers/', methods=['GET'])
def forumListUsers():
    try:
        cursor = cnx.cursor()
        # OPTIONAL
        since_id = request.args.get('since_id')
        limit = request.args.get('limit')
        order = request.args.get('order')

        short_name = request.args.get('forum')
        forum = ForumQueries.fetchBySlug(cursor, short_name)
        users = UserQueries.fetchForumUsers(cursor, short_name, since_id, limit, order)

        for user in users:
            completeUser(user)

        return jsonify({'code': Codes.OK, 'response': users})
    except DBNotFound as exc:
        return jsonify({'code': Codes.NOT_FOUND, 'response': exc.message})
    except (RequiredMissing, KeyError) as exc:
        return jsonify({'code': Codes.INVALID_QUERY, 'response': exc.message})
    except (IntegrityError, OperationalError) as exc:
        return jsonify({'code': Codes.INCORRECT_DB_QUERY, 'response': exc.msg})
    except Exception as exc:
        return jsonify({'code': Codes.UNKNOWN_ERROR, 'response': exc.message})


#------------------------------------------

# TODO +, CONSTRANT ON PARENT DOESN't WORK PROPERLY
@app.route('/post/create/', methods=['POST'])
def createPost():
    try:
        cursor = cnx.cursor()
        inData = request.get_json(force=True)

    #   OPTIONAL
        parent = getValueOrZero(inData, 'parent')
        isApproved = getValueOrFalse(inData, 'isApproved')
        isHighlighted = getValueOrFalse(inData, 'isHighlighted')
        isEdited = getValueOrFalse(inData, 'isEdited')
        isSpam = getValueOrFalse(inData, 'isSpam')
        isDeleted = getValueOrFalse(inData, 'isDeleted')

    #   REQUIRED
        date = inData['date']
        threadID = inData['thread']
        message = inData['message']
        user = inData['user']
        forum = inData['forum']
        # HERE KeyError Exception can be raised

        requiredParams = [date, threadID, message, user, forum]
        optionalParams = [isApproved, isHighlighted, isEdited, isSpam, isDeleted, parent]

        PostQueries.create(cursor, requiredParams, optionalParams)
        cnx.commit()
        postID = cursor.lastrowid
        post = PostQueries.fetchById(cursor, postID)
        response = completePost(post)
        return jsonify({'code': Codes.OK, 'response': response})

    except DBNotFound as exc:
        return jsonify({'code': Codes.NOT_FOUND, 'response': exc.message})
    except (RequiredMissing, KeyError) as exc:
        return jsonify({'code': Codes.INVALID_QUERY, 'response': exc.message})
    except (OperationalError, IntegrityError) as exc:
        return jsonify({'code': Codes.INCORRECT_DB_QUERY, 'response': exc.msg})
    except Exception as exc:
        return jsonify({'code': Codes.UNKNOWN_ERROR, 'response': exc.message})

# TODO +, USER FOLLOWERS PROBLEMS, I CANNOT CREATE POSTS
@app.route('/post/details/', methods=['GET'])
def postDetails():
    try:
        cursor = cnx.cursor()
        related = getListOrEmpty(request.args, 'related')
        postID = request.args.get('post')

        post = PostQueries.fetchById(cursor, postID)
        response = completePost(post)
        if 'user' in related:
            response.update({'user': completeUser(UserQueries.fetchByEmail(cursor, post['user']))})
        if 'thread' in related:
            response.update({'thread': completeThread(ThreadQueries.fetchById(cursor, post['thread']))})
        if 'forum' in related:
            response.update({'forum': completeForum(post['forum'])})
        return jsonify({'code': Codes.OK, 'response': response})
    except DBNotFound as exc:
        return jsonify({'code': Codes.NOT_FOUND, 'response': exc.message})
    except (RequiredMissing, KeyError) as exc:
        return jsonify({'code': Codes.INVALID_QUERY, 'response': exc.message})
    except (IntegrityError, OperationalError) as exc:
        return jsonify({'code': Codes.INCORRECT_DB_QUERY, 'response': exc.msg})
    except Exception as exc:
        return jsonify({'code': Codes.UNKNOWN_ERROR, 'response': exc.message})

# TODO + SORT, COMPLETE POSTS WONT WORK
@app.route('/post/list/', methods=['GET'])
def postList():
    try:
        cursor = cnx.cursor()
        since = request.args.get('since')
        limit = request.args.get('limit')
        order = request.args.get('order')

        short_name = request.args.get('forum')
        thread = request.args.get('thread')

        if(short_name is None) and (thread is None):
            raise RequiredMissing('forum name or thread')
        if thread is not None:
            posts = PostQueries.fetchThreadPosts(cursor, thread, since, limit, order)
        else:
            posts = PostQueries.fetchForumPosts(cursor, short_name, since, limit, order)
        for post in posts:
            post = completePost(post)
        return jsonify({'code': Codes.OK, 'response': posts})
    except DBNotFound as exc:
        return jsonify({'code': Codes.NOT_FOUND, 'response': exc.message})
    except (RequiredMissing, KeyError) as exc:
        return jsonify({'code': Codes.INVALID_QUERY, 'response': exc.message})
    except (IntegrityError, OperationalError) as exc:
        return jsonify({'code': Codes.INCORRECT_DB_QUERY, 'response': exc.msg})
    except Exception as exc:
        return jsonify({'code': Codes.UNKNOWN_ERROR, 'response': exc.message})

# TODO DECREASE NUMBER OF POSTS FOR THEAD/FORUM
@app.route('/post/remove/', methods=['POST'])
def postRemove():
    try:
        cursor = cnx.cursor()
        inData = request.get_json(force=True)
        postId = inData['post']
        PostQueries.setDeleted(cursor, postId, True)
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

# TODO INCREASE NUMBER OF POSTS FOR THEAD/FORUM
@app.route('/post/restore/', methods=['POST'])
def postRestore():
    try:
        cursor = cnx.cursor()
        inData = request.get_json(force=True)
        postId = inData['post']
        PostQueries.setDeleted(cursor, postId, False)
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

# TODO +, DONT SEE ANY BREAKS
@app.route('/post/update/', methods=['POST'])
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

# TODO +, MUST BE WORKING
@app.route('/post/vote/', methods=['POST'])
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
#------------------------------------------

@app.route('/thread/close/', methods=['POST'])
def threadClose():
    try:
        cursor = cnx.cursor()
        inData = request.get_json(force=True)
        threadId = inData['thread']

        ThreadQueries.setClosed(cursor, threadId, True)
        cnx.commit()
        return jsonify({'code': Codes.OK, 'response': threadId})
    except:
        pass

# TODO EXC WORKS! DATE SETUP FAILED
@app.route('/thread/create/', methods=['POST'])
def threadCreate():
    try:
        cursor = cnx.cursor()
        inData = request.get_json(force=True)


        forumName = inData['forum']
        title = inData['title']
        isClosed = inData['isClosed']
        user = inData['user']
        dateCreated = inData['date']
        message = inData['message']
        slug = inData['slug']

        isDeleted = getValueOrFalse(inData, 'isDeleted')

        forum = ForumQueries.fetchBySlug(cursor, forumName)
        forumID = forum[0]

        requiredParams = [title, isClosed, user, dateCreated, message, slug, forumID]
        optionalParams = [isDeleted]
        ThreadQueries.create(cursor, requiredParams, optionalParams)
        cnx.commit()


        total = list(requiredParams)
        total.append(optionalParams)
        # total = requiredParams + optionalParams
        return jsonify({'code': Codes.OK, 'response': total})
    except:
        pass
# TODO HAVEN"T TESTED RELATED. NEED TO ASK MAX ABOUT IT
@app.route('/thread/details/', methods=['GET'])
def threadDetails():
    try:
        cursor = cnx.cursor()
        related = request.args.get('related')
        threadID = int(request.args.get('thread'))

        thread = ThreadQueries.fetchById(cursor, threadID)
        try:
            if 'user' in related:
                user = UserQueries.fetchByEmail(cursor, thread['user'])
                thread['user'] = user
            if 'forum' in related:
                forum = ForumQueries.fechById(cursor, thread['forum'])
                thread['forum'] = forum
        except TypeError as exc:
            pass
        #     RELATED IS EMPTY TODO
        return jsonify({'code': Codes.OK, 'response': thread})
    except:
        pass

# TODO EXC WORKS
@app.route('/thread/open/', methods=['POST'])
def threadOpen():
    try:
        cursor = cnx.cursor()
        inData = request.get_json(force=True)
        threadId = inData['thread']

        ThreadQueries.setClosed(cursor, threadId, False)
        cnx.commit()
        return jsonify({'code': Codes.OK, 'response': threadId})
    except:
        pass

# TODO UPDATE DOESNT WORK
@app.route('/thread/remove/', methods=['POST'])
def threadRemove():
    try:
        cursor = cnx.cursor()
        inData = request.get_json(force=True)
        threadId = inData['thread']

        ThreadQueries.setDeleted(cursor, threadId, True)
        cnx.commit()
        return jsonify({'code': Codes.OK, 'response': threadId})
    except:
        pass

@app.route('/thread/restore/', methods=['POST'])
def threadRestore():
    try:
        cursor = cnx.cursor()
        inData = request.get_json(force=True)
        threadId = inData['thread']

        ThreadQueries.setDeleted(cursor, threadId, False)
        cnx.commit()
        return jsonify({'code': Codes.OK, 'response': threadId})
    except:
        pass

@app.route('/thread/update/', methods=['POST'])
def threadUpdate():
    try:
        cursor = cnx.cursor()
        inData = request.get_json(force=True)

        threadID = inData['thread']
        message = inData['message']
        slug = inData['slug']

        ThreadQueries.updMsgSlug(cursor, threadID, message, slug)
        cnx.commit()
        thread = ThreadQueries.fetchById(cursor, threadID)
        return jsonify({'code': Codes.OK, 'response': thread})
    except:
        pass

@app.route('/thread/vote/', methods=['POST'])
def threadVote():
    try:
        cursor = cnx.cursor()
        inData = request.get_json(force=True)

        threadId = inData['thread']
        vote = inData['vote']

        try:
            if (vote == 1):
                liked = True
            elif (vote == -1):
                liked = False
            else:
                # GFY and give me normal data
                pass

        except TypeError:
            # Here will be return
            pass;

        ThreadQueries.updVote(cursor, threadId, liked)
        cnx.commit()
        thread = ThreadQueries.fetchById(cursor, threadId)
        return jsonify({'code': Codes.OK, 'response': thread})
    except:
        pass

@app.route('/thread/subscribe/', methods=['POST'])
def threadSubscribe():
    try:
        cursor = cnx.cursor()
        inData = request.get_json(force=True)

        user = inData['user']
        threadID = inData['thread']
        cnx.commit()
        ThreadQueries.subscribe(cursor, threadID, user)
        responce = {threadID, user}

        return jsonify({'code': Codes.OK, 'response': responce})
    except:
        pass

@app.route('/thread/unsubscribe/', methods=['POST'])
def threadUnsubscribe():
    try:
        cursor = cnx.cursor()
        inData = request.get_json(force=True)

        user = inData['user']
        threadID = inData['thread']
        cnx.commit()
        ThreadQueries.unsubscribe(cursor, threadID, user)
        responce = {threadID, user}

        return jsonify({'code': Codes.OK, 'response': responce})
    except:
        pass
#------------------------------------------

# TODO +, STILL NO ERRORS
@app.route('/user/create/', methods=['POST'])
def userCreate():
    try:
        cursor = cnx.cursor()
        inData = request.get_json(force=True)

        about = inData['about']
        name = inData['name']
        username = inData['username']
        user = inData['email']
        isAnonymous = getValueOrFalse(inData, 'isAnonymous')

        requiredParams = [about, name, username, user]
        optionalParams = [isAnonymous]
        UserQueries.create(cursor, requiredParams, optionalParams)
        cnx.commit()
        userId = cursor.lastrowid
        response = {"about": about, "email": user, "id": userId,
                    "isAnonymous": isAnonymous, "name": name, "username": username}
        return jsonify({'code': Codes.OK, 'response': response})
    except DBNotFound as exc:
        return jsonify({'code': Codes.NOT_FOUND, 'response': exc.message})
    except (RequiredMissing, KeyError) as exc:
        return jsonify({'code': Codes.INVALID_QUERY, 'response': exc.message})
    except (OperationalError, IntegrityError) as exc:
        return jsonify({'code': Codes.INCORRECT_DB_QUERY, 'response': exc.msg})
    except Exception as exc:
        return jsonify({'code': Codes.UNKNOWN_ERROR, 'response': exc.message})

# TODO +, MAYBE LISTS FOR FOLLOWERS, FOLLOWEE, SUBSCRIPTIONS WILL NOT BE RIGHT OPTION
@app.route('/user/details/', methods=['GET'])
def userDetails():
    try:
        cursor = cnx.cursor()
        email = request.args.get('user')
        user = UserQueries.fetchByEmail(cursor, email)
        response = completeUser(user)
        return jsonify({'code': Codes.OK, 'response': response})
    except DBNotFound as exc:
        return jsonify({'code': Codes.NOT_FOUND, 'response': exc.message})
    except (RequiredMissing, KeyError) as exc:
        return jsonify({'code': Codes.INVALID_QUERY, 'response': exc.message})
    except (OperationalError, IntegrityError) as exc:
        return jsonify({'code': Codes.INCORRECT_DB_QUERY, 'response': exc.msg})
    except Exception as exc:
        return jsonify({'code': Codes.UNKNOWN_ERROR, 'response': exc.message})

# TODO +, ALMOST WORKING, SOMEHOW FOLLOWER is written like "follower" not 'follower'
@app.route('/user/follow/', methods=['POST'])
def userFollow():
    try:
        cursor = cnx.cursor()
        inData = request.get_json(force=True)

        followee = inData['followee']
        follower = inData['follower']

        UserQueries.follow(cursor, followee, follower)
        cnx.commit()

        user = UserQueries.fetchByEmail(cursor, follower)
        response= completeUser(user)

        return jsonify({'code': Codes.OK, 'response': response})
    except DBNotFound as exc:
        return jsonify({'code': Codes.NOT_FOUND, 'response': exc.message})
    except (RequiredMissing, KeyError) as exc:
        return jsonify({'code': Codes.INVALID_QUERY, 'response': exc.message})
    except (OperationalError, IntegrityError) as exc:
        return jsonify({'code': Codes.INCORRECT_DB_QUERY, 'response': exc.msg})
    except Exception as exc:
        return jsonify({'code': Codes.UNKNOWN_ERROR, 'response': exc.__str__()})

# TODO PYTHON LOGICS IS OK, DB DOESN"T WORK HERE
@app.route('/user/listFollowers/', methods=['GET'])
def userListFollowers():
    try:
        cursor = cnx.cursor()
        since_id = request.args.get('since_id')
        limit = request.args.get('limit')
        order = request.args.get('order')

        user = request.args.get('user')
        followers = UserQueries.getUsersFollowers(cursor, user, since_id, limit, order)
        response = []
        for follower in followers:
            response.append(completeUser(follower))

        return jsonify({'code': Codes.OK, 'response': response})
    except DBNotFound as exc:
        return jsonify({'code': Codes.NOT_FOUND, 'response': exc.message})
    except (RequiredMissing, KeyError) as exc:
        return jsonify({'code': Codes.INVALID_QUERY, 'response': exc.message})
    except (OperationalError, IntegrityError) as exc:
        return jsonify({'code': Codes.INCORRECT_DB_QUERY, 'response': exc.msg})
    except Exception as exc:
        return jsonify({'code': Codes.UNKNOWN_ERROR, 'response': exc.__str__()})

# TODO PYTHON LOGICS IS OK, DB DOESN"T WORK HERE
@app.route('/user/listFollowee/', methods=['GET'])
def userListFollowee():
    try:
        cursor = cnx.cursor()
        since_id = request.args.get('since_id')
        limit = request.args.get('limit')
        order = request.args.get('order')

        user = request.args.get('user')
        followee = UserQueries.getUsersFollowee(cursor, user, since_id, limit, order)
        response = []
        for human in followee:
            response.append(completeUser(human))

        return jsonify({'code': Codes.OK, 'response': response})
    except DBNotFound as exc:
        return jsonify({'code': Codes.NOT_FOUND, 'response': exc.message})
    except (RequiredMissing, KeyError) as exc:
        return jsonify({'code': Codes.INVALID_QUERY, 'response': exc.message})
    except (OperationalError, IntegrityError) as exc:
        return jsonify({'code': Codes.INCORRECT_DB_QUERY, 'response': exc.msg})
    except Exception as exc:
        return jsonify({'code': Codes.UNKNOWN_ERROR, 'response': exc.__str__()})

# TODO LIMIT PROBLEMS IN SQL
@app.route('/user/listPosts/', methods=['GET'])
def userListFollowee():
    try:
        cursor = cnx.cursor()
        since = request.args.get('since_id')
        limit = request.args.get('limit')
        order = request.args.get('order')

        user = request.args.get('user')
        posts = PostQueries.fetchUserPosts(cursor, user, since, limit, order)
        response = []
        for post in posts:
            response.append(completePost(post))

        return jsonify({'code': Codes.OK, 'response': response})
    except DBNotFound as exc:
        return jsonify({'code': Codes.NOT_FOUND, 'response': exc.message})
    except (RequiredMissing, KeyError) as exc:
        return jsonify({'code': Codes.INVALID_QUERY, 'response': exc.message})
    except (OperationalError, IntegrityError) as exc:
        return jsonify({'code': Codes.INCORRECT_DB_QUERY, 'response': exc.msg})
    except Exception as exc:
        return jsonify({'code': Codes.UNKNOWN_ERROR, 'response': exc.__str__()})

# TODO SAME THING WITH DOUBLE QUOTES
@app.route('/user/unfollow/', methods=['POST'])
def userUnfollow():
    try:
        cursor = cnx.cursor()
        inData = request.get_json(force=True)
        followee = inData['followee']
        follower = inData['follower']

        UserQueries.unfollow(cursor, followee, follower)
        cnx.commit()
        user = UserQueries.fetchByEmail(cursor, follower)
        response = completeUser(user)

        return jsonify({'code': Codes.OK, 'response': response})
    except DBNotFound as exc:
        return jsonify({'code': Codes.NOT_FOUND, 'response': exc.message})
    except (RequiredMissing, KeyError) as exc:
        return jsonify({'code': Codes.INVALID_QUERY, 'response': exc.message})
    except (OperationalError, IntegrityError) as exc:
        return jsonify({'code': Codes.INCORRECT_DB_QUERY, 'response': exc.msg})
    except Exception as exc:
        return jsonify({'code': Codes.UNKNOWN_ERROR, 'response': exc.__str__()})

# TODO CHECK!
@app.route('/user/updateProfile/', methods=['POST'])
def userUpdate():
    try:
        cursor = cnx.cursor()
        inData = request.get_json(force=True)

        about = inData['about']
        email = inData['user']
        name = inData['name']

        UserQueries.updateProfile(cursor, email, about, name)
        cnx.commit()
        user = UserQueries.fetchByEmail(cursor, email)
        response = completeUser(user)
        return jsonify({'code': Codes.OK, 'response': response})
    except DBNotFound as exc:
        return jsonify({'code': Codes.NOT_FOUND, 'response': exc.message})
    except (RequiredMissing, KeyError) as exc:
        return jsonify({'code': Codes.INVALID_QUERY, 'response': exc.message})
    except (OperationalError, IntegrityError) as exc:
        return jsonify({'code': Codes.INCORRECT_DB_QUERY, 'response': exc.msg})
    except Exception as exc:
        return jsonify({'code': Codes.UNKNOWN_ERROR, 'response': exc.__str__()})





@app.route("/", methods=['GET', 'POST'])
def tester():
    tml = "forum.html"
    return render_template(tml)


if __name__ == "__main__":
    app.run(debug=True)
