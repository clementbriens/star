from elasticsearch import Elasticsearch
import configparser
import os
from utils.es_mapping import mapping, user_mapping
from datetime import datetime

class STAR_ES():
    def __init__(self):
        config = configparser.ConfigParser()
        config.read('config.ini')
        self.es_cloud_id = config['es']['es_cloud_id']
        self.es_cloud_user = config['es']['es_cloud_user']
        self.es_cloud_pass = config['es']['es_cloud_pass']
        self.es_cloud_port = config['es']['es_cloud_port']

    #connecting to ELK and returning the object
    def load_es(self):
        try:
            self.es = Elasticsearch(
            [self.es_cloud_id],
            http_auth=(self.es_cloud_user, self.es_cloud_pass),
            scheme="https", port=self.es_cloud_port,)
            print('[*] Connected to ES.')
            return self.es
        except:
            print('[!] Could not connect to ES.')

    #parsing out some unwanted data
    def parse_tweet(self, tweet):
        data = dict()
        for key in tweet.keys():
            if key in mapping:
                data[key] = tweet[key]
            if 'star' in key:
                data[key] = tweet[key]
        for key in tweet['user'].keys():
            if key in user_mapping:
                data['user.{}'.format(key)] = tweet['user'][key]
        data['entities'] = dict()
        for entity in ["urls", "user_mentions", "symbols", "hashtags"]:
            for e in tweet['entities'][entity]:
                data['entities'][entity] = list()
                if entity in ['hashtags']:
                    data['entities'][entity].append(e['text'])
                elif entity in ['user_mentions']:
                    data['entities'][entity].append(e['screen_name'])
                elif entity in ['urls', 'symbols']:
                    data['entities'][entity].append(e)
        data['timestamp'] = datetime.strptime(tweet['created_at'],'%a %b %d %H:%M:%S +0000 %Y')
        data['user.created_at'] =  datetime.strptime(data['user.created_at'],'%a %b %d %H:%M:%S +0000 %Y')
        return data
