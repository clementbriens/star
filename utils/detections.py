import dateparser
from datetime import datetime

string_categories = ['strings', 'mentions', 'urls', 'user_name', 'screen_name', 'hashtags', 'description']
math_categories = ['date', 'account_date', 'account_followers', 'account_friends']
bool_categories = ['verified', 'protected', 'geo_enabled', 'contributors_enabled',
'is_translator', 'is_translation_enabled', 'profile_background_tile', 'profile_use_background_image',
'has_extended_profile', 'default_profile', 'default_profile_image', 'profile_background_tile',
'following', 'follow_request_sent', 'notifications', 'is_quote_status',
'favorited', 'retweeted', 'possibly_sensitive', 'possibly_sensitive_appealable']

all_categories = string_categories + math_categories + bool_categories
all_categories.append('condition')

def get_string_cat_detection(cat, tweet):
    if cat == 'strings':
        for t in ['text', 'full_text']:
            if t in tweet.keys():
                detection = tweet[t]
    elif cat == 'mentions':
        detection = [x['screen_name'] for x in tweet['entities']['user_mentions']]
    elif cat == 'user_name':
        detection = tweet['user']['name']
    elif cat == 'screen_name':
        detection = tweet['user']['screen_name']
    elif cat == 'hashtags':
        detection = [x['text']for x in tweet['entities']['hashtags']]
    elif cat == 'description':
        detection = tweet['user']['description']
    else:
        print('Error: category "{}" not recognized.'.format(cat))
        detection = None
    return detection

def get_math_cat_detection(cat, tweet):
    if cat == 'date':
        # detection = dateparser.parse(tweet['created_at'])
        detection = datetime.strptime(tweet['created_at'],'%a %b %d %H:%M:%S +0000 %Y')
    elif cat == "account_date":
        detection = datetime.strptime(tweet['user']['created_at'],'%a %b %d %H:%M:%S +0000 %Y')
    elif cat == "account_followers":
        detection = int(tweet['user']['followers_count'])
    elif cat == "account_friends":
        detection = int(tweet['user']['friends_count'])
    return detection

def get_bool_cat_detection(cat, tweet):
    if cat in ['favorited', 'retweeted', 'possibly_sensitive', 'possibly_sensitive_appealable']:
        return tweet[cat]
    else:
        return tweet['user'][cat]
