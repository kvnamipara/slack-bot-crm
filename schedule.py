# -*- coding: utf-8 -*-
import pymongo,os
import datetime
from slackclient import SlackClient

MONGO_URL = os.environ.get('MONGO_URL')

def check_for_midnight():
    time = datetime.datetime.utcnow()
    seconds = int(time.strftime('%H'))*3660 + int(time.strftime('%M'))*60
    mdb_connection = pymongo.MongoClient(MONGO_URL)
    db = mdb_connection['slack-bot']
    for item in db.users.find():
        if item['tz_offset'] + seconds == 86400 or item['tz_offset'] + seconds == 0:
            res = db.authed_teams.find_one({'team_id':item['team_id']})
            token = res['bot_token']
            channel_id = item['channel_id']
            send_message(token,item['team_id'],channel_id,'hi <@'+item['name']+'>')
    mdb_connection.close()

def send_message(token,team_id,channel_id, message):
    slack_client = SlackClient(token)
    slack_client.api_call(
        "chat.postMessage",
        channel=channel_id,
        text=message,
        username='chitterchat',
        icon_emoji=':robot_face:'
    )
