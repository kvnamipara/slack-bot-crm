# -*- coding: utf-8 -*-
import os
import pymongo
import datetime
from slackclient import SlackClient

MONGO_URL = os.environ.get('MONGO_URL')

class Bot(object):
    def __init__(self):
        super(Bot, self).__init__()
        self.name = "pythonbot"
        self.emoji = ":robot_face:"
        self.oauth = {"client_id": os.environ.get("CLIENT_ID"),
                      "client_secret": os.environ.get("CLIENT_SECRET"),
                      "scope": "bot"}
        self.verification = os.environ.get("VERIFICATION_TOKEN")
        self.client = SlackClient("")

    def auth(self, code):
        auth_response = self.client.api_call(
                                "oauth.access",
                                client_id=self.oauth["client_id"],
                                client_secret=self.oauth["client_secret"],
                                code=code)
        if auth_response['ok']:
            team_id = auth_response["team_id"]
            bot_token = auth_response["bot"]["bot_access_token"]
            self.insert_to_db('authed_teams',{'team_id':team_id,'bot_token':bot_token})
            token = self.find_bot_token(team_id)
            self.client = SlackClient(token)
            self.first_response_to_existing_users()
            self.find_all_channel(team_id)


    def find_all_channel(self,team_id):
        print 'inserting channels'
        request = self.client.api_call("channels.list")
        if request['ok']:
            for item in request['channels']:
                if item['is_channel'] == True and item['is_archived']==False:
                    self.insert_to_db('channels',{'team_id':team_id,'channel_id':item['id'],'name':item['name']})
                    if item['name']=='general':
                        self.update_many_db('users','team_id',team_id,'channel_id',item['id'])


    def first_response_to_existing_users(self):
        print 'inserting users'
        request = self.client.api_call("users.list")
        if request['ok']:
            for item in request['members']:
                if item['deleted']==False and item['is_bot']==False:
                    if item['name']!='slackbot':
                        self.insert_to_db('users',{'team_id':item['team_id'],'user_id':item['id'],
                        'name':item['name'],'tz_offset':item['tz_offset']})


    def remove_team(self,team_id):
        self.remove_from_db('authed_teams','team_id',team_id)
        self.remove_from_db('users','team_id',team_id)
        self.remove_from_db('channels','team_id',team_id)




    def find_bot_token(self,team_id):
        mgdb = pymongo.MongoClient(MONGO_URL)
        db = mgdb['slack-bot']
        res = db['authed_teams'].find_one({'team_id':team_id})
        mgdb.close()
        return res['bot_token']

    def insert_to_db(self,collection,data):
        mgdb = pymongo.MongoClient(MONGO_URL)
        db = mgdb['slack-bot']
        db[collection].insert_one(data)
        mgdb.close()

    def find_in_db(self,collection,parameter,value):
        mgdb = pymongo.MongoClient(MONGO_URL)
        db = mgdb['slack-bot']
        if db[collection].find_one({parameter,value})==None:
            mgdb.close()
            return True  #not present in db
        return False

    def remove_from_db(self,collection,parameter,value):
        mgdb = pymongo.MongoClient(MONGO_URL)
        db = mgdb['slack-bot']
        db[collection].delete_many({parameter: value})
        mgdb.close()

    def update_in_db(self,collection,match_parameter,matching_value,update_parameter,new_value):
        mgdb = pymongo.MongoClient(MONGO_URL)
        db = mgdb['slack-bot']
        db[collection].find_one_and_update({match_parameter:matching_value}, {"$set": {update_parameter: new_value}})
        mgdb.close()

    def update_many_db(self,collection,match_parameter,matching_value,update_parameter,new_value):
        mgdb = pymongo.MongoClient(MONGO_URL)
        db = mgdb['slack-bot']
        db[collection].update_many({match_parameter:matching_value}, {"$set": {update_parameter: new_value}})
        mgdb.close()
