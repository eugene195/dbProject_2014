__author__ = 'eugene'

from flask import Flask

from ForumAPI import forum_api
from UserAPI import user_api
from PostAPI import post_api
from ThreadAPI import thread_api
from flaskext.mysql import MySQL
from helperFuncs import *

app.register_blueprint(forum_api, url_prefix = PREFIX + '/forum')
app.register_blueprint(user_api, url_prefix = PREFIX + '/user')
app.register_blueprint(post_api, url_prefix = PREFIX + '/post')
app.register_blueprint(thread_api, url_prefix = PREFIX + '/thread')


@app.route(PREFIX+ "/clear/", methods=['POST'])
@connect_to_DB('clear')
def clear(connect, cursor):
    print("Entered")
    inData = request.get_json(force=True)
    UtilQueries.clear(cursor)
    connect.commit()
    print("Exited")
    return jsonify({'code': Codes.OK, 'response': "OK"})

if __name__ == "__main__":
    app.run(debug=True, port=5000)
