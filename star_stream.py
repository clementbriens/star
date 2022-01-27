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
        print(status_code)
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

    except ChunkedEncodingError:
        stream_tweets(tweet_queue)

star = STAR()

def load_all_rules(rule_path):
    rules = list()
    if rule_path:
        pass
    else:
        rule_path = './rules/'
    for rule in os.listdir(rule_path):
        rules.append(star.read_rule(rule_path + rule))
    return rules

def process_tweets(tweets_queue, rules, output, output_path, verbose):
    while True:
        tweet = tweets_queue.get()
        # Do something with the tweet
        #print(tweet)
        for rule in rules:
            hit = star.scan_tweet(tweet, rule)
            if hit['hit']:
                print(Fore.GREEN + 'Hit on ' + Fore.RED + rule['title'] + Fore.GREEN + ': {}\n'.format(tweet['id']))
                if verbose:
                    print(Fore.YELLOW + '\tHandle:', tweet['user']['screen_name'])
                    print(Fore.YELLOW + '\tFollowers:', tweet['user']['followers_count'])
                    print(Fore.YELLOW + '\tText:')
                    print(Fore.GREEN + '\t' + tweet['text'])
                print(Style.RESET_ALL)
                hit['rule'] = rule['title']
                tweet['star_hit'] = hit
                if output == 'json':
                    try:
                        filename = '{}/{}.json'.format(output_path, tweet['id'])
                        with open(filename, 'w') as f:
                            json.dump(tweet, f)
                            if verbose:
                                print('\n\tSaved tweet to {}\n'.format(filename))
                    except:
                        print('[!] Could not save Tweet.\n')
        tweets_queue.task_done()

def run(mode, lang = None, terms = None, output = None, output_path = None, rules_path = None, verbose = None):
    rules = load_all_rules(rules_path)
    print('All STAR rules ({}) loaded.'.format(len(rules)))
    print('Starting tweet collection...\n')
    tweet_queue = Queue()
    Thread(target=stream_tweets, args=(tweet_queue, mode, lang, terms), daemon=True).start()
    process_tweets(tweet_queue, rules, output, output_path, verbose)

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

    args = vars(parser.parse_args())
    run(mode = args['mode'],
    lang = args['lang'],
    terms = args['terms'],
    output = args['output'],
    output_path = args['path'],
    rules_path = args['rules'],
    verbose = args['verbose'])
    #run(mode = 'sample', lang = 'en', terms = [], output = 'json', output_path = 'hits', verbose = True)
