__author__ = 'eugene'

from flask import Flask

from ForumAPI import forum_api
from UserAPI import user_api
from PostAPI import post_api
from ThreadAPI import thread_api

from helperFuncs import *

app = Flask(__name__)
app.register_blueprint(forum_api, url_prefix = PREFIX + '/forum')
app.register_blueprint(user_api, url_prefix = PREFIX + '/user')
app.register_blueprint(post_api, url_prefix = PREFIX + '/post')
app.register_blueprint(thread_api, url_prefix = PREFIX + '/thread')




@app.route(PREFIX+ "/clear/", methods=['POST'])
@connect_to_DB('clear')
def clear(connect):
    inData = request.get_json(force=True)
    cursor = connect.cursor()
    UtilQueries.clear(cursor)
    connect.commit()
    return jsonify({'code': Codes.OK, 'response': "OK"})

if __name__ == "__main__":
    app.run(debug=True, port=5000)
