import sys
import yaml
import json
from utils import detections, sentiment_analysis
import dateparser
import argparse
import pandas as pd
import re

class STAR():

    def __init__(self, args = None):
        print('[*] Simple Twitter Analysis Rules.')
        if type(args) == dict:
            self.args = args
            print(args)
        elif args:
            self.args = vars(args)
        else:
            self.args = None

        if self.args['sentiment']:
            self.sa = sentiment_analysis.Sentiment_Analyzer()

    def check_rule(self, rule):
        try:
            condition = rule['detection']['condition']
        except:
            print('No condition detected in rule.')
            return False
        if condition:
            for key in rule['detection'].keys():
                if key not in detections.all_categories:
                    print('{}: {} is not a recognized category.'.format(rule['title'], key))
                    return False
                if key not in condition and key != 'condition':
                    print('{}: {} is not included in condition logic. Please revise rule.'.format(rule['title'], key))
                    return False
        return True


    def read_rule(self, path):
        # try:
        with open(path, 'r') as stream:
            rule = yaml.safe_load(stream)
            check = self.check_rule(rule)
            if check:
                print('- Loaded {}.'.format(rule['title']))
                return rule
            else:
                sys.exit()
        # except:
        #     print('{} is not a valid STAR rule.'.format(path))
        #     return None

    def scan_tweet(self, tweet, rule):
        # try:
        condition = ''
        categories = {}
        # go through each string category defined in detections.py
        # if the string category is in the rule, check whether the string is
        # in the tweet's field
        for cat in detections.string_categories:
            if cat in rule['detection'].keys():
                categories[cat] = {}
                detection = detections.get_string_cat_detection(cat, tweet)
                for string in rule['detection'][cat]:
                    if detection:
                        if string in detection:
                            categories[cat][string] = True
                        else:
                            categories[cat][string] = False
                    else:
                        categories[cat][string] = False

        # collecting sentiment data if required
        sent = None
        if self.args['sentiment']:
            if 'full_text' in tweet.keys():
                text = tweet['full_text']
            else:
                text = tweet['text']
            if tweet['lang'] == "en":
                sent = self.sa.sentiment(text)
            else:
                sent = self.sa.translate_and_analyze(text)

        # go through each math category defined in detections.py
        # if the string category is in the rule, check whether the string is
        # in the range of the tweet's field
        for cat in detections.math_categories:
            if cat in rule['detection'].keys():
                categories[cat] = {}
                if cat.startswith('sentiment'):
                    detection = detections.get_math_cat_detection(cat, tweet, sent)
                else:
                    detection = detections.get_math_cat_detection(cat, tweet)
                for math in rule['detection'][cat]:
                    if 'date' in cat:
                        date = dateparser.parse(math.split(' ')[1])
                        if math.startswith('before'):
                            if date > detection:
                                categories[cat][math] = True
                            else:
                                categories[cat][math] = False
                        elif math.startswith('after'):
                            if date < detection:
                                categories[cat][math] = True
                            else:
                                categories[cat][math] = False
                    else:
                        if cat.startswith('sentiment'):
                            value = float(math.split(' ')[1])
                        else:
                            value = int(math.split(' ')[1])
                        if math.startswith('min'):
                            if value <= detection:
                                categories[cat][math] = True
                            else:
                                categories[cat][math] = False
                        if math.startswith('max'):
                            if value >= detection:
                                categories[cat][math] = True
                            else:
                                categories[cat][math] = False

        # go through each boolean category defined in detections.py
        # if the boolean category is in the rule, check whether the boolean is
        # in the tweet field
        for cat in detections.bool_categories:
            if cat in rule['detection'].keys():
                categories[cat] = {}
                detection = detections.get_bool_cat_detection(cat, tweet)
                if rule['detection'][cat] == detection:
                    categories[cat][bool] = True
                else:
                    categories[cat][bool] = False

        for cat in detections.regex_categories:
            if cat in rule['detection'].keys():
                categories[cat] = {}
                detection = detections.get_regex_cat_detection(cat, tweet)
                for regex in rule['detection'][cat]:
                    if re.findall(regex, detection):
                        categories[cat][regex] = True
                    else:
                        categories[cat][regex] = False

        # understand the defined logic in the conditions string
        if rule['detection']['condition']:
            conditions = list()
            condition_bools = list()
            cond_split = rule['detection']['condition'].split(' ')
            if len(cond_split) > 3:
                i = 0
                cid = 0
                for c in cond_split:
                    if c == 'of':
                        conditions.append({'threshold' : cond_split[i-1],
                        'category' : cond_split[i+1], 'cid' : cid})
                        cid += 1
                    if c in ['and', 'or']:
                        condition_bools.append({'a' : cid -1, 'bool' : c, 'b': cid})
                    i +=1
            else:
                condition_bools.append({'a' : 0, 'bool' : 'same', 'b' : 0})
                conditions.append({'threshold' : cond_split[0],
                'category' : cond_split[2], 'cid' : 0})

        final_condition_bools = {}
        # print('final_condition_bools:', final_condition_bools)
        for condition in conditions:
            if condition['category'] in categories.keys():
                nb_true = 0
                for dict in categories[condition['category']].keys():

                    if categories[condition['category']][dict]:
                        nb_true += 1

                final_condition_bools[condition['cid']] = {}
                if condition['threshold'] == 'none' or condition['threshold'] == 0:
                    if nb_true == 0:
                        final_condition_bools[condition['cid']]['bool'] = True
                    else:
                        final_condition_bools['cid']['bool'] = False
                elif condition['threshold'] == 'all':
                    if nb_true == len(categories[condition['category']].keys()):
                        final_condition_bools[condition['cid']]['bool'] = True
                    else:
                        final_condition_bools[condition['cid']]['bool'] = False
                elif condition['threshold'] == 'any':
                    if nb_true > 0:
                        final_condition_bools[condition['cid']]['bool'] = True
                    else:
                        final_condition_bools[condition['cid']]['bool'] = False

                else:
                    if int(condition['threshold']) <= int(nb_true):
                        final_condition_bools[condition['cid']]['bool'] = True
                    else:
                        final_condition_bools[condition['cid']]['bool'] = False

        final_conditions = list()

        for cb in condition_bools:
            if cb['bool'] == 'same':
                final_conditions.append(str(final_condition_bools[0]['bool']))
            else:
                final_condition = "{} {} {}".format(final_condition_bools[cb['a']]['bool'], cb['bool'], final_condition_bools[cb['b']]['bool'])
                if eval(final_condition):
                    final_conditions.append('True')
                else:
                    final_conditions.append('False')

        if len(cond_split) == 3:
            end_condition = final_conditions[0]
        else:
            end_condition = ' and '.join(final_conditions)

        end_condition_bool = eval(end_condition)
        matches = list()
        if end_condition_bool:
            for key in final_condition_bools.keys():
                if final_condition_bools[key]:
                    for condition in conditions:
                        if condition['cid'] == key:
                            for key in categories[condition['category']].keys():
                                if categories[condition['category']][key]:
                                    matches.append({'category' : condition['category'], 'detection' : key})
        # else:
            # print('No match found.')
        if self.args['sentiment']:
            hit ={'hit' : end_condition_bool, 'matches' : matches, 'sentiment_data' : sent}
        else:
            hit ={'hit' : end_condition_bool, 'matches' : matches}
        if self.args and 'fields' in self.args.keys():
            for field in self.args['fields']:
                if field in tweet['user'].keys():
                    hit[field] = tweet['user'][field]
                else:
                    hit[field] = tweet[field]

        return hit
        # except:
        #     print('{} rule not formatted correctly.'.format(rule['title']))

    def bulk_scan(self, path, rule):
        pass

    def main(self):
        if self.args['rule']:
            rule = self.read_rule(self.args['rule'])
        if self.args['input']:
            if self.args['input'].endswith('json'):
                try:
                    print('Loading Tweets...')
                    tweets = json.load(self.args['input'])
                except:
                    try:
                        with open(self.args['input']) as file:
                            tweets = list(map(json.loads, file))
                    except:
                        print('Error loading JSON file {}. Are you sure it is formatted correctly?'.format(self.args['input']))
                        sys.exit()

        output_data = list()
        x = 0
        y = 0
        for tweet in tweets:
            print('{}/{} tweets scanned | {} hits'.format(x, len(tweets), y), end = '\r')
            hit = self.scan_tweet(tweet, rule)
            print(hit)
            if hit['hit']:
                y += 1
                output_data.append(hit)

            x += 1
        if 'output' in self.args.keys():
            if self.args['output'].endswith('json'):
                with open(self.args['output'], 'w') as file:
                    json.dump(output_data, file,  indent=4)
            if self.args['output'].endswith('csv'):
                df = pd.DataFrame(output_data)
                df.to_csv(self.args['output'])
        print('\nDone.')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-r', '--rule', metavar='r',
                        help='STAR Rules to use for scanning a tweet')
    parser.add_argument('-i', '--input', metavar='i', help="Input for tweet")
    parser.add_argument('-o', '--output', metavar='o', help='Output for scan results')
    parser.add_argument('-f', '--fields', metavar='f', nargs = '+', help='Fields to be returned in the scan results')
    parser.add_argument('-s', '--sentiment', default = False, action = 'store_true')

    args = parser.parse_args()

    star = STAR({'sentiment' : True, 'input' : 'hits/1486730163127607313.json', 'rule' : 'rules/test/test_sent.yml'})
    star.main()
