from twython import TwythonStreamer
import configparser
from star import STAR
import time
import sys
import os
from threading import Thread
from queue import Queue
from requests.exceptions import ChunkedEncodingError
from colorama import Fore, Back, Style
import json
import argparse

class TwitterStream(TwythonStreamer):

    def __init__(self, consumer_key, consumer_secret, token, token_secret, tqueue):
        self.tweet_queue = tqueue
        super(TwitterStream, self).__init__(consumer_key, consumer_secret, token, token_secret)

    def on_success(self, data):
        if 'text' in data:
            self.tweet_queue.put(data)

    def on_error(self, status_code, data, headers):
        if status_code == 420:
            print('[!] Twitter API is throttling attempts to reopen a stream- please wait several minutes and try again.')
        self.disconnect()
        sys.exit()

def stream_tweets(tweets_queue, mode, lang = None, keywords = None):
    # Input your credentials below
    config = configparser.ConfigParser()
    config.read('config.ini')
    consumer_key = config['twitter']['api_key']
    consumer_secret = config['twitter']['api_secret']
    token = config['twitter']['access_token']
    token_secret = config['twitter']['access_secret']
    try:
        stream = TwitterStream(consumer_key, consumer_secret, token, token_secret, tweets_queue)
        if mode == 'sample':
            stream.statuses.sample(language = lang)
        elif mode == 'filter':
            stream.statuses.filter(track = keywords)
        else:
            print('[!] No streaming mode specified.')
            sys.exit()

    except ChunkedEncodingError:
        stream_tweets(tweets_queue, mode = mode, lang = lang, keywords = keywords)

def load_all_rules(rule_path, star):
    rules = list()
    if rule_path:
        pass
    else:
        rule_path = './rules/'
    # for rule in os.listdir(rule_path):
    #     if rule.endswith('.yml'):
    #         rules.append(star.read_rule(rule_path + rule))
    for root, dirs, files in os.walk(rule_path):
        for file in files:
            if file.endswith(".yml"):
                 rules.append(star.read_rule(os.path.join(root, file)))
    return rules

def process_tweets(tweets_queue, rules, output, output_path, verbose, es, index, star_es, star):
# def process_tweets(**kwargs):
    while True:
        tweet = tweets_queue.get()
        # Do something with the tweet
        #print(tweet)
        tweet['star'] = list()
        hits = list()
        for rule in rules:
            hit = star.scan_tweet(tweet, rule)
            if hit['hit']:
                print(Fore.GREEN + 'Hit on ' + Fore.RED + rule['title'] + Fore.GREEN + ': {}'.format(tweet['id']))
                if verbose:
                    print(Fore.YELLOW + '\tHandle:', tweet['user']['screen_name'])
                    print(Fore.YELLOW + '\tFollowers:', tweet['user']['followers_count'])
                    print(Fore.YELLOW + '\tText:')
                    print(Fore.GREEN + '\t' + tweet['text'])
                print(Style.RESET_ALL)
                hit['rule'] = rule['title']

                tweet['star'].append(hit)
                hits.append(hit)
        tweet['star_rules'] = [h['rule'] for h in hits]
        tweet['star_nb_hits'] = len(hits)

        if tweet['star_nb_hits'] > 0:
            if 'sentiment_data' in hit.keys():
                hit['sentiment_data'] = hit['sentiment_data']


            for key in tweet['user'].keys():
                tweet['user.{}'.format(key)] = tweet['user'][key]

            if output == 'json':
                try:
                    filename = '{}/{}.json'.format(output_path, tweet['id'])
                    with open(filename, 'w') as f:
                        json.dump(tweet, f)
                        if verbose:
                            print('\tSaved tweet to {}\n'.format(filename))
                except:
                    if verbose:
                        print('\tCould not save tweet.\n')
                    pass
            elif output == 'es':
                es.index(index, id = tweet['id'], body = star_es.parse_tweet(tweet))
                if verbose:
                    print('\tSaved tweet to ES.\n')

        tweets_queue.task_done()
        if tweets_queue.qsize() > 5000:
            tweet_queue = Queue()

def run(mode, lang = None, terms = None, output = None, output_path = None, rules_path = None, verbose = None, index = None, sentiment = None):
    es = None
    if output == 'es':
        from star_es import STAR_ES
        star_es = STAR_ES()
    es = star_es.load_es()

    star = STAR({'sentiment' : sentiment})
    rules = load_all_rules(rules_path, star)
    print('[*] All STAR rules ({}) loaded.'.format(len(rules)))
    print('[*] Starting tweet collection...\n')
    tweet_queue = Queue()
    Thread(target=stream_tweets, args=(tweet_queue, mode, lang, terms), daemon=True).start()
    if es:
        process_tweets(tweet_queue, rules, output, output_path, verbose, es, index, star_es, star)
    else:
        process_tweets(tweet_queue, rules, output, output_path, verbose, None, None, star_es, star)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-m', '--mode', required = True,
                        help="Streaming modes as per Twitter's API docs. sample|filter")
    parser.add_argument('-l', '--lang', default = False, help = "Language for stream sampling. en|es|ru|fr...")
    parser.add_argument('-t', '--terms', default = False, nargs='+', help = "Terms/keywords for stream filtering.")
    parser.add_argument('-o', '--output', default = None, help = 'Output format for scan results. json')
    parser.add_argument('-p', '--path', default = None, help = 'Output path for scan results. json')
    parser.add_argument('-r', '--rules', default = None, help = 'Path for STAR rules to scan for.')
    parser.add_argument('-v', '--verbose', default = False, action='store_true', help = 'Verbosity level in CLI output.')
    parser.add_argument('-i', '--index', default = None, help = 'Elasticsearch index for results.')
    parser.add_argument('-s', '--sentiment', default = False, action = 'store_true')

    args = vars(parser.parse_args())
    run(mode = args['mode'],
    lang = args['lang'],
    terms = args['terms'],
    output = args['output'],
    output_path = args['path'],
    rules_path = args['rules'],
    verbose = args['verbose'],
    index = args['index'],
    sentiment = args['sentiment'])
    #run(mode = 'sample', lang = 'en', terms = [], output = 'json', output_path = 'hits', verbose = True)
