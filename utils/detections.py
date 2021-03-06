import dateparser
from datetime import datetime, date

string_categories = ['strings', 'mentions', 'urls', 'user_name', 'screen_name',
'hashtags', 'description', 'lang', 'source', 'location']
math_categories = ['date', 'account_date', 'account_followers', 'account_friends',
'nb_mentions', 'nb_tweets', 'tweets_per_day', 'tweets_per_week', 'sentiment_compound',
'sentiment_negative', 'sentiment_neutral', 'sentiment_positive', 'favourites_count', 'statuses_count', 'utc_offset' ]
bool_categories = ['verified', 'protected', 'geo_enabled', 'contributors_enabled',
'is_translator', 'is_translation_enabled', 'profile_background_tile', 'profile_use_background_image',
'has_extended_profile', 'default_profile', 'default_profile_image', 'profile_background_tile',
'following', 'follow_request_sent', 'notifications', 'is_quote_status',
'favorited', 'retweeted', 'possibly_sensitive', 'possibly_sensitive_appealable']
regex_categories = ['re_' + x for x in string_categories]

all_categories = string_categories + math_categories + bool_categories + regex_categories
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
    elif cat == 'lang':
        detection = tweet['user']['lang']
    elif cat == 'source':
        detection = tweet['source']
    elif cat == 'location':
        detection = tweet['user']['location']
    else:
        print('Error: category "{}" not recognized.'.format(cat))
        detection = None
    return detection

def get_math_cat_detection(cat, tweet, sent = None):

    if cat == 'date':
        # detection = dateparser.parse(tweet['created_at'])
        detection = datetime.strptime(tweet['created_at'],'%a %b %d %H:%M:%S +0000 %Y')
    elif cat == "account_date":
        detection = datetime.strptime(tweet['user']['created_at'],'%a %b %d %H:%M:%S +0000 %Y')
    elif cat == "account_followers":
        detection = int(tweet['user']['followers_count'])
    elif cat == "account_friends":
        detection = int(tweet['user']['friends_count'])
    elif cat == "nb_mentions":
        detection = len([x['screen_name'] for x in tweet['entities']['user_mentions']])
    elif cat == "nb_tweets":
        detection = int(tweet['user']['statuses_count'])
    elif cat == "favourites_count":
        detection = int(tweet['user']['favourites_count'])
    elif cat == "statuses_count":
        detection = int(tweet['user']['statuses_count'])
    elif cat == "utc_offset":
        detection = round(int(tweet['user']['utc_offset']) / 3600, 0)
    elif cat == "tweets_per_day":
        now = datetime.today()
        create_date = datetime.strptime(tweet['user']['created_at'],'%a %b %d %H:%M:%S +0000 %Y')
        try:
            detection = round(int(tweet['user']['statuses_count']) / (now - create_date).days, 0)
        #in case account was created today
        except:
            detection = int(tweet['user']['statuses_count'])
    elif cat == "tweets_per_week":
        now = datetime.today()
        create_date = datetime.strptime(tweet['user']['created_at'],'%a %b %d %H:%M:%S +0000 %Y')
        try:
            detection = round(int(tweet['user']['statuses_count']) / (now - create_date).weeks, 0)
        #in case account was created this week
        except:
            detection = int(tweet['user']['statuses_count'])
    elif 'sentiment' in cat:
        detection = float(sent[cat])
    return detection

def get_bool_cat_detection(cat, tweet):
    if cat in ['favorited', 'retweeted', 'possibly_sensitive', 'possibly_sensitive_appealable']:
        return tweet[cat]
    else:
        return tweet['user'][cat]

def get_regex_cat_detection(cat, tweet):
    return get_string_cat_detection(cat[3:], tweet)
