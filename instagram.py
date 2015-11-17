import datetime
import operator
import os
import requests
import sys

from flask import Flask, request, render_template
app = Flask(__name__)

ACCESS_TOKEN = os.environ.get('ACCESS_TOKEN', None)
FOLLOWERS_ROOT = "https://api.instagram.com/v1/users/%d/followed-by?access_token=%s"
LAST_POST_ROOT = "https://api.instagram.com/v1/users/%d/media/recent/?access_token=%s&count=1"

@app.route("/")
def home():
    return render_template("home.html")

def get_followers(user_id):
    '''
    Returns the followers for a given Instagram user.
    '''
    response = requests.get(FOLLOWERS_ROOT % (int(user_id), ACCESS_TOKEN)).json()
    if "data" in response and response["data"]:
        return response["data"]

    return None

def last_post_time(user_id):
    '''
    Returns the time of the last post for a given Instagram user.
    '''
    response = requests.get(LAST_POST_ROOT % (int(user_id), ACCESS_TOKEN)).json()
    if "data" in response and response["data"]:
        return response["data"][0]["created_time"]

    return None

def get_day_from_timestamp(timestamp):
    '''
    Returns day of the week for a given timestamp.
    '''
    return datetime.datetime.utcfromtimestamp(int(timestamp)).strftime('%A')

def get_hour_from_timestamp(timestamp):
    '''
    Returns hour of the day for a given timestamp
    '''
    return datetime.datetime.utcfromtimestamp(int(timestamp)).strftime('%H')

@app.route("/process", methods=["GET"])
def main():
    DAY_COUNT = {}
    HOUR_COUNT = {}
    user_id = int(request.args.get('userid'))
    username = request.args.get('username')
    followers_list = get_followers(user_id)
    if followers_list is None:
        return "Cannot fetch information for the user as it is not available."

    for follower in followers_list:
        timestamp = last_post_time(follower["id"])
        if not timestamp:
            # skipping this user
            continue

        last_post_day = get_day_from_timestamp(timestamp)
        if last_post_day not in DAY_COUNT:
            DAY_COUNT[last_post_day] = 0

        DAY_COUNT[last_post_day] += 1
        last_post_hour = get_hour_from_timestamp(timestamp)
        if last_post_hour not in HOUR_COUNT:
            HOUR_COUNT[last_post_hour] = 0

        HOUR_COUNT[last_post_hour] += 1

    most_active_day = max(DAY_COUNT.iteritems(), key=operator.itemgetter(1))[0]
    most_active_hour = int(max(HOUR_COUNT.iteritems(), key=operator.itemgetter(1))[0])
    return render_template("response.html", time=most_active_hour, day=most_active_day)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
