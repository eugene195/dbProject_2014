__author__ = 'eugene'

#
def setSortType(sort):
    if sort is None or sort == 'flat':
        sort = ''
    elif sort == 'tree':
        sort = ', parent ASC'
    elif sort == 'parent_tree':
        sort = ', parent ASC'
    return sort

class DBNotFound(Exception):
    def __init__(self, value):
        self.message = value

class RequiredMissing(Exception):
    def __init__(self, param):
        self.message = "Required parameter '%s' not found" % param

class BadFormat(Exception):
    def __init__(self, param):
        self.message = "Wrong input format, parameter '%s'" % param

def getIntOrDefault(obj, default):
    try:
        obj = int(obj)
    except Exception:
        obj = default
    return obj

def getOrDefault(variable, default):
    if variable is None:
        return default
    else:
        return variable

class UtilQueries:
    @staticmethod
    def clear(cursor):
        query = "SET FOREIGN_KEY_CHECKS=0"
        cursor.execute(query)
        tableList = ['Forum', 'User', 'Thread', 'Post', 'Follow', 'Subscribe']

        for table in tableList:
            # query = '''DELETE %s.* FROM %s;''' % (table, table)
            query = "TRUNCATE TABLE `%s`;" %table
            cursor.execute(query)

        query = "SET FOREIGN_KEY_CHECKS=1"
        cursor.execute(query)


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
    def create(cursor, required):
        query = "INSERT INTO `User` (about, name, username, email, isAnonymous) VALUES ('%s', '%s', '%s', '%s', %s);"\
                % (required['about'], required['name'], required['username'], required['email'], required['isAnonymous'])
        cursor.execute(query)


    @staticmethod
    def updateProfile(cursor, email, about, name):
        query = "UPDATE User SET about = '%s', name = '%s' WHERE User.email = '%s'" % (about, name, email)
        cursor.execute(query)


    @staticmethod
    def follow(cursor, followee, follower):
        query = "INSERT INTO Follow (follower, followee) VALUES ('%s', '%s');" % (follower, followee)
        cursor.execute(query)


    @staticmethod
    def unfollow(cursor, followee, follower):
        query = "DELETE FROM Follow WHERE follower = '%s' AND followee = '%s';" % (follower, followee)
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


    @staticmethod
    def getUsersFollowers(cursor, user, since_id, limit, order):
        limit = getIntOrDefault(limit, 1000)
        order = getOrDefault(order, 'DESC')
        since_id = getIntOrDefault(since_id, 0)
        query = "SELECT * FROM Follow as F JOIN `User` as U ON F.follower = U.email " \
                "WHERE followee = '%s' AND U.id >= %d ORDER BY name %s LIMIT %d" % (user, since_id, order, limit)
        cursor.execute(query)
        followers = cursor.fetchall()
        return followers


    @staticmethod
    def getUsersFollowee(cursor, user, since_id, limit, order):
        limit = getIntOrDefault(limit, 1000)
        order = getOrDefault(order, 'DESC')
        since_id = getIntOrDefault(since_id, 0)
        query = "SELECT * FROM Follow as F JOIN `User` as U ON F.followee = U.email " \
                "WHERE follower = '%s' AND U.id >= %d ORDER BY name %s LIMIT %d" % (user, since_id, order, limit)
        cursor.execute(query)
        followers = cursor.fetchall()
        return followers


    @staticmethod
    def fetchForumUsers(cursor, forum, since_id, limit, order):
        since_id = getIntOrDefault(since_id, 0)
        limit = getIntOrDefault(limit, 1000)
        order = getOrDefault(order, 'DESC')

        query = '''SELECT *
                    FROM `User`
                    WHERE id >= %d AND
                    email IN (
                    SELECT DISTINCT `user` FROM `Post`
                    WHERE `forum` = '%s'
                    ) ORDER BY `User`.`name` %s LIMIT %d
                    ''' % (since_id, forum, order, limit)

        cursor.execute(query)
        forumUsers = cursor.fetchall()
        return forumUsers


    @staticmethod
    def getSubscriptions(cursor, email):
        query = "SELECT thread FROM Subscribe WHERE Subscribe.user = '%s' " % email
        cursor.execute(query)
        subscriptions = cursor.fetchall()
        return subscriptions

class ForumQueries:
    @staticmethod
    def create(cursor, name, short_name, user):
        query = "INSERT INTO Forum (name, short_name, user) VALUES ('%s', '%s', '%s');" % (name, short_name, user)
        cursor.execute(query)


    @staticmethod
    def fetchBySlug(cursor, short_name):
        short_name = getOrDefault(short_name, '')
        query = "SELECT * FROM Forum WHERE Forum.short_name = '%s'" % short_name
        cursor.execute(query)

        forum = cursor.fetchone()
        if forum is None:
            raise DBNotFound("Forum with short_name '%s' not found" % short_name)
        return forum

    @staticmethod
    def fechById(cursor, forumID):
        query = "SELECT * FROM Forum WHERE Forum.forumID = %d;" % forumID
        cursor.execute(query)
        forum = cursor.fetchone()
        return forum


class PostQueries:
    @staticmethod
    def create(cursor, required, optional):
        query = '''INSERT INTO Post (date, thread, message, user, forum,
                isApproved, isHighlighted, isEdited, isSpam, isDeleted, parent
                ) VALUES ('%s', %d, '%s', '%s', '%s',
                %s, %s, %s, %s, %s, '%s');''' \
                % (
                    required['date'], required['thread'],
                    required['message'], required['user'], required['forum'],
                    optional['isApproved'], optional['isHighlighted'], optional['isEdited'],
                    optional['isSpam'], optional['isDeleted'], optional['parent']
                  )

        cursor.execute(query)

    @staticmethod
    def update_path(cursor, id, parent_id, isCorrect):
        if isCorrect:
            query = '''UPDATE Post SET path = id WHERE id = %s''' % (str(id))
            cursor.execute(query)
        else:
            query = '''SELECT path, children FROM Post WHERE id = %d LIMIT 1''' % (parent_id)
            cursor.execute(query)
            parent = cursor.fetchone()
            parent_path = parent[0]
            childId = parent[1] + 1
            childPath = parent_path + "." + str(childId)
            query = '''UPDATE Post SET path = '%s' WHERE id = %d''' % (childPath, id)
            cursor.execute(query)
            query = '''UPDATE Post SET children = children + 1 WHERE id = %d''' % (parent_id)
            cursor.execute(query)

    @staticmethod
    def fetchById(cursor, id):
        query = "SELECT * FROM Post WHERE Post.id = %s;" % id
        cursor.execute(query)

        post = cursor.fetchone()
        if post is None:
            raise DBNotFound("Post with id %d not found" % id)
        return post


    @staticmethod
    def setDeleted(cursor, id, deleted):
        query = "UPDATE Post SET isDeleted = %s WHERE Post.id = %d" % (deleted, id)
        cursor.execute(query)


    @staticmethod
    def threadUpdatePostCount(cursor, id, value):
        query = "UPDATE Thread SET posts = posts %s WHERE Thread.id = %d" % (value, id)
        cursor.execute(query)

    @staticmethod
    def updMessage(cursor, id, message):
        query = "UPDATE Post SET message = '%s' WHERE Post.id = %d" % (message, id)
        cursor.execute(query)


    @staticmethod
    def updVote(cursor, id, isLiked):
        if(isLiked == True):
            query = "UPDATE Post SET points = points + 1, likes = likes + 1 WHERE Post.id = %d" % id
        else:
            query = "UPDATE Post SET points = points - 1, dislikes = dislikes + 1 WHERE Post.id = %d" % id
        cursor.execute(query)


    @staticmethod
    def fetchForumPosts(cursor, forum, since, limit, order, sort):
        since = getOrDefault(since, '2000-01-01 00:00:00')
        limit = getIntOrDefault(limit, 1000)
        order = getOrDefault(order, 'DESC')
        sort = setSortType(sort)

        query = "SELECT * FROM Post WHERE Post.forum = '%s' AND Post.`date` > '%s' ORDER BY `date` %s %s LIMIT %s "\
                % (forum, since, order, sort, limit)
        cursor.execute(query)
        posts = cursor.fetchall()
        return posts


    @staticmethod
    def     fetchThreadPosts(cursor, thread, since, limit, order, sort):
        since = getOrDefault(since, '2000-01-01 00:00:00')
        limit = getOrDefault(limit, '1000')
        sort = setSortType(sort)
        order = getOrDefault(order, 'DESC')

        query = "SELECT * FROM Post WHERE Post.thread = %s AND Post.date > '%s' ORDER BY date %s %s LIMIT %s "\
                % (thread, since, order, sort, limit)
        cursor.execute(query)
        posts = cursor.fetchall()
        return posts


    @staticmethod
    def fetchUserPosts(cursor, user, since, limit, order):
        since = getOrDefault(since, '2000-01-01 00:00:00')
        limit = getIntOrDefault(limit, 1000)
        order = getOrDefault(order, 'DESC')

        query = "SELECT * FROM Post WHERE Post.user = '%s' AND Post.`date` > '%s' ORDER BY `date` %s LIMIT %s "\
                % (user, since, order, limit)
        cursor.execute(query)
        posts = cursor.fetchall()
        return posts


class ThreadQueries:
    @staticmethod
    def fetchById(cursor, id):
        query = "SELECT * FROM Thread WHERE Thread.id = %s;" % id
        cursor.execute(query)
        thread = cursor.fetchone()
        if thread is None:
            raise DBNotFound("Thread with id %d not found" % id)
        return thread


    @staticmethod
    def setClosed(cursor, id, isClosed):
        query = "UPDATE Thread SET isClosed = %s WHERE Thread.id = %d" % (isClosed, id)
        cursor.execute(query)


    @staticmethod
    def setDeleted(cursor, id, deleted):
        if deleted:
            query = "UPDATE Thread SET isDeleted = True, removedPosts = posts, posts = 0 WHERE Thread.id = %d" % (id)
        else:
            query = "UPDATE Thread SET isDeleted = False, posts = removedPosts, removedPosts = 0 WHERE Thread.id = %d" % (id)
        cursor.execute(query)
        query = "UPdATE Post SET isDeleted = %s WHERE Post.thread = '%s'" % (deleted, id)
        cursor.execute(query)


    @staticmethod
    def create(cursor, required):
        query = "INSERT INTO Thread (title, isClosed, user, `date`, message, slug, forum, isDeleted) " \
                "VALUES ('%s', %s, '%s', '%s', '%s', '%s', '%s', %s);" % \
                (required['title'], required['isClosed'], required['user'], required['date'],
                 required['message'], required['slug'], required['forum'], required['isDeleted'])
        cursor.execute(query)


    @staticmethod
    def updMsgSlug(cursor, id, message, slug):
        query = "UPDATE Thread SET message = '%s', slug = '%s' WHERE Thread.id = %d" % (message, slug, id)
        cursor.execute(query)


    @staticmethod
    def updVote(cursor, id, isLiked):
        if(isLiked == True):
            query = "UPDATE Thread SET points = points + 1, likes = likes + 1 WHERE Thread.id = %d" % id
        else:
            query = "UPDATE Thread SET points = points - 1, dislikes = dislikes + 1 WHERE Thread.id = %d" % id
        cursor.execute(query)


    @staticmethod
    def subscribe(cursor, id, user):
        query = "INSERT INTO Subscribe (user, thread) VALUES ('%s', %d);" % (user, id)
        cursor.execute(query)


    @staticmethod
    def unsubscribe(cursor, id, user):
        query = "DELETE FROM Subscribe WHERE thread = %d AND user = '%s';" % (id, user)
        cursor.execute(query)


    @staticmethod
    def fetchForumThreads(cursor, forum, since, limit, order):
        since = getOrDefault(since, '2000-01-01 00:00:00')
        limit = getIntOrDefault(limit, 1000)
        order = getOrDefault(order, 'DESC')

        query = "SELECT * FROM Thread WHERE Thread.forum = '%s' AND Thread.date > '%s' ORDER BY date %s LIMIT %s "\
                % (forum, since, order, limit)
        cursor.execute(query)
        threads = cursor.fetchall()
        return threads


    @staticmethod
    def fetchUserThreads(cursor, user, since, limit, order):
        since = getOrDefault(since, '2000-01-01 00:00:00')
        limit = getIntOrDefault(limit, 1000)
        order = getOrDefault(order, 'DESC')

        query = "SELECT * FROM Thread WHERE Thread.user = '%s' AND Thread.date > '%s' ORDER BY date %s LIMIT %s "\
                % (user, since, order, limit)
        cursor.execute(query)
        threads = cursor.fetchall()
        return threads