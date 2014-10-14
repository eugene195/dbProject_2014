__author__ = 'eugene'



class DBNotFound(Exception):
    def __init__(self, value):
        self.message = value
class RequiredMissing(Exception):
    def __init__(self, param):
        self.message = "Required parameter '%s' not found" % param

class BadFormat(Exception):
    def __init__(self, param):
        self.message = "Wrong input format, parameter '%s'" % param

def isStated(parameter):
    if(parameter == None) or (parameter == ""):
        return False
    else:
        return parameter

def getOrDefault(variable, default):
    if variable is None:
        return default
    else:
        return variable


class UserQueries:
    @staticmethod
    def fetchByEmail(cursor, email):
        query = "SELECT * FROM `User` WHERE `User`.email = '%s'" % email
        cursor.execute(query)
        user = cursor.fetchone()
        if user is None:
            raise DBNotFound("User with email '%s' not found" % email)
        return user

    @staticmethod
    def fetchByUsername(cursor, username):
        query = "SELECT userId, about, isAnonymous, realName, username, email `User` WHERE `User`.username = '%s'" % username
        cursor.execute(query)
        user = cursor.fetchone()
        return user

    @staticmethod
    def create(cursor, required, optional):
        query = "INSERT INTO `User` (about, realName, username, email) VALUES ('%s', '%s', '%s', '%s');" % \
                (required[0], required[1], required[2], required[3])
        cursor.execute(query)

    @staticmethod
    def updateProfile(cursor, email, about, name):
        query = "UPDATE User SET about = '%s', realName = '%s' WHERE User.email = '%s'" % (about, name, email)
        cursor.execute(query)

    @staticmethod
    def follow(cursor, followee, follower):
        query = "INSERT INTO Follow (follower, followee) VALUES (%s, %s);" % (follower, followee)
        cursor.execute(query)

    @staticmethod
    def unfollow(cursor, followee, follower):
        query = "DELETE FROM Follow WHERE follower = '%s' AND folowee = '%s';" % (follower, followee)
        cursor.execute(query)

    @staticmethod
    def getFollowers(cursor, user):
        query = "SELECT follower FROM Follow WHERE followee = '%s'" % user
        cursor.execute(query)
        followers = cursor.fetchall()
        return followers

    @staticmethod
    def getFollowee(cursor, user):
        query = "SELECT followee FROM Follow WHERE follower = '%s'" % user
        cursor.execute(query)
        followere = cursor.fetchall()
        return followere


    # TODO LIMIT!!
    @staticmethod
    def getUsersFollowers(cursor, user, since_id, limit, order):
        return []
        limit = getOrDefault(limit, 1000)
        order = getOrDefault(order, "DESC")
        since_id = getOrDefault(since_id, 0)
        query = "SELECT * FROM Follow as F JOIN `User` as U ON F.followee = U.email " \
                "WHERE follower = '%s' AND U.id > %d ORDER BY realName '%s LIMIT %d" % (user, since_id, order, limit)
        cursor.execute(query)
        followers = cursor.fetchall()
        return followers

    # TODO LIMIT!!
    @staticmethod
    def getUsersFollowee(cursor, user, since_id, limit, order):
        return []
        limit = getOrDefault(limit, 1000)
        order = getOrDefault(order, "DESC")
        since_id = getOrDefault(since_id, 0)
        query = "SELECT * FROM Follow as F JOIN `User` as U ON F.followee = U.email " \
                "WHERE followee = '%s' AND U.id > %d ORDER BY realName '%s LIMIT %d" % (user, since_id, order, limit)
        cursor.execute(query)
        followers = cursor.fetchall()
        return followers


    # TODO TROUBLES WITH LIMIT
    @staticmethod
    def fetchForumUsers(cursor, forum, since_id, limit, order):
        return []
        since_id = getOrDefault(since_id, 0)
        limit = getOrDefault(limit, 1000)
        order = getOrDefault(order, "DESC")

        query = "SELECT * FROM `User` WHERE `User`.userID > %d AND EXISTS " \
                "(SELECT * FROM Post WHERE Post.forum = '%s' AND Post.user = `User`.email) " \
                "ORDER BY `User`.realName '%s' LIMIT '%s';" % (since_id, forum, order, limit)
        cursor.execute(query)
        forumUsers = cursor.fetchall()
        if forumUsers is None:
            raise DBNotFound("Users for this forum '%s' not found" % forum)
        return forumUsers

    # TODO SUBSCRIPTIONS
    @staticmethod
    def getSubscriptions(cursor, user):
        return []





class ForumQueries:
    @staticmethod
    def create(cursor, forumName, shortName, user):
        query = "INSERT INTO Forum (forumName, shortName, user) VALUES ('%s', '%s', '%s');" % (forumName, shortName, user)
        cursor.execute(query)

    @staticmethod
    def fetchBySlug(cursor, shortName):
        query = "SELECT * FROM Forum WHERE Forum.shortName = '%s'" % shortName
        cursor.execute(query)
        forum = cursor.fetchone()
        if forum is None:
            raise DBNotFound("Forum with shortname '%s' not found" % shortName)
        return forum

    @staticmethod
    def fechById(cursor, forumID):
        query = "SELECT * FROM Forum WHERE Forum.forumID = %d;" % forumID
        cursor.execute(query)
        forum = cursor.fetchone()
        return forum

class PostQueries:
    @staticmethod
    #     OPTIONAL PARAMS TODO
    # 0 - date, 1 - threadId 2 - message, 3 - email, 4 - forumID
    def create(cursor, required, optional):
        query = "INSERT INTO Post (dateCreated, thread, message, user, forum," \
                "isApproved, isHighlighted, isEdited, isSpam, isDeleted, parent" \
                ") VALUES ('%s', %d, '%s', '%s', '%s', " \
                "'%s', '%s', '%s', '%s', '%s', %d);" % \
                (required[0], required[1], required[2], required[3], required[4],
                optional[0], optional[1], optional[2], optional[3], optional[4], optional[5])
        cursor.execute(query)

    @staticmethod
    def fetchById(cursor, postID):
        query = "SELECT * FROM Post WHERE Post.postID = %d;" % postID
        cursor.execute(query)
        post = cursor.fetchone()
        if post is None:
            raise DBNotFound("Post with id %d not found" % postID)
        return post

    @staticmethod
    def setDeleted(cursor, postID, deleted):
        query = "UPDATE Post SET isDeleted = '%s' WHERE Post.postID = %d" % (deleted, postID)
        cursor.execute(query)

    @staticmethod
    def updMessage(cursor, postID, message):
        query = "UPDATE Post SET message = '%s' WHERE Post.postID = %d" % (message, postID)
        cursor.execute(query)

    @staticmethod
    def updVote(cursor, postId, isLiked):
        if(isLiked == True):
            query = "UPDATE Post SET points = points + 1, likes = likes + 1 WHERE Post.postID = %d" % postId
        else:
            query = "UPDATE Post SET points = points - 1, dislikes = dislikes + 1 WHERE Post.postID = %d" % postId
        cursor.execute(query)

    # TODO LIMIT
    # TODO ADD SORT
    @staticmethod
    def fetchForumPosts(cursor, forum, since, limit, order):
        since = getOrDefault(since, "0000-00-00 00:00:00")
        limit = getOrDefault(limit, 1000)
        # sort = getOrDefault(sort, "FLAT")
        order = getOrDefault(order, "DESC")
        #     TODO: ADD SORT!!

        query = "SELECT * FROM Post WHERE Post.forum = '%s' AND Post.dateCreated > '%s' ORDER BY dateCreated '%s' LIMIT %d "\
                % (forum, since, order, limit)
        cursor.execute(query)
        posts = cursor.fetchall()
        return posts

        # TODO ADD SORT
    @staticmethod
    def fetchThreadPosts(cursor, thread, since, limit, order):

        since = getOrDefault(since, "0000-00-00 00:00:00")
        limit = getOrDefault(limit, 1000)
        # sort = getOrDefault(sort, "FLAT")
        order = getOrDefault(order, "DESC")
        #     TODO: ADD SORT!!

        query = "SELECT * FROM Post WHERE Post.thread = %d AND Post.dateCreated > '%s' ORDER BY dateCreated '%s' LIMIT %d "\
                % (thread, since, order, limit)
        cursor.execute(query)
        posts = cursor.fetchall()
        return posts

    # TODO LIMIT
    @staticmethod
    def fetchUserPosts(cursor, user, since, limit, order):
        return []
        since = getOrDefault(since, "0000-00-00 00:00:00")
        limit = getOrDefault(limit, 1000)
        order = getOrDefault(order, "DESC")

        query = "SELECT * FROM Post WHERE Post.user = '%s' AND Post.dateCreated > '%s' ORDER BY dateCreated '%s' LIMIT %d "\
                % (user, since, order, limit)
        cursor.execute(query)
        posts = cursor.fetchall()
        return posts

class ThreadQueries:
    @staticmethod
    def fetchById(cursor, threadID):
        query = "SELECT * FROM Thread WHERE Thread.threadID = %d;" % threadID
        cursor.execute(query)
        thread = cursor.fetchone()
        if thread is None:
            raise DBNotFound("Thread with id %d not found" % threadID)
        return thread

    @staticmethod
    def setClosed(cursor, threadId, isClosed):
        query = "UPDATE Thread SET isClosed = '%s' WHERE Thread.threadID = %d" % (isClosed, threadId)
        cursor.execute(query)

    @staticmethod
    def setDeleted(cursor, threadID, deleted):
        query = "UPDATE Thread SET isDeleted = '%s' WHERE Thread.threadID = %d" % (deleted, threadID)
        cursor.execute(query)

    @staticmethod
    def create(cursor, required, optional):
        query = "INSERT INTO Thread (title, isClosed, user, dateCreated, message, slug, forum, isDeleted) " \
                "VALUES ('%s', '%s', '%s', '%s', '%s', '%s', %d, '%s');" % \
                (required[0], required[1], required[2], required[3], required[4], required[5], required[6], optional[0])
        cursor.execute(query)

    @staticmethod
    def updMsgSlug(cursor, threadID, message, slug):
        query = "UPDATE Thread SET message = '%s', slug = '%s' WHERE Thread.threadID = %d" % (message, slug, threadID)
        cursor.execute(query)

    @staticmethod
    def updVote(cursor, threadID, isLiked):
        if(isLiked == True):
            query = "UPDATE Thread SET points = points + 1, likes = likes + 1 WHERE Thread.threadID = %d" % threadID
        else:
            query = "UPDATE Thread SET points = points - 1, dislikes = dislikes + 1 WHERE Thread.threadID = %d" % threadID
        cursor.execute(query)

    @staticmethod
    def subscribe(cursor, threadID, user):
        query = "INSERT INTO Subscribe (user, threadID) VALUES ('%s', %d);" % (user, threadID)
        cursor.execute(query)

    @staticmethod
    def unsubscribe(cursor, threadID, user):
        query = "DELETE FROM Subscribe WHERE threadID = %d AND user = '%s';" % (threadID, user)
        cursor.execute(query)

    # TODO LIMIT PROBLEMS
    @staticmethod
    def fetchForumThreads(cursor, forum, since, limit, order):
        return []
        since = getOrDefault(since, "0000-00-00 00:00:00")
        limit = getOrDefault(limit, 1000)
        order = getOrDefault(order, "DESC")

        query = "SELECT * FROM Post WHERE Post.forum = '%s' AND Post.dateCreated > '%s' ORDER BY dateCreated '%s' LIMIT %d "\
                % (forum, since, order, limit)
        cursor.execute(query)
        threads = cursor.fetchall()
        if threads is None:
            raise DBNotFound("Threads for this forum '%s' not found" % forum)
        return cursor.fetchall()


# TODO GET SUBSCRIBER BY ID??