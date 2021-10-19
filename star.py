import sys
import yaml
import json
from tweet import tweet
from utils import detections
import dateparser


class STAR():


    def __init__(self):
        print('Simple Twitter Analysis Rules.')

    def read_rule(self, path):
        try:
            with open(path, 'r') as stream:
                rule = yaml.safe_load(stream)
            return rule

        except:
            print('{} is not a valid STAR rule.'.format(path))
            return None

    def scan_tweet(self, tweet, rule):
        condition = ''
        categories = {}

        for cat in detections.string_categories:
            if rule['detection'][cat]:
                categories[cat] = {}
                detection = detections.get_string_cat_detection(cat, tweet)
                for string in rule['detection'][cat]:
                    if string in detection:
                        categories[cat][string] = True
                    else:
                        categories[cat][string] = False

        for cat in detections.math_categories:
            if rule['detection'][cat]:
                categories[cat] = {}
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
        for cat in detections.bool_categories:
            if cat in rule['detection'].keys():
                categories[cat] = {}
                detection = detections.get_bool_cat_detection(cat, tweet)
                bool = rule['detection'][cat]
                if bool == detection:
                    categories[cat][bool] = True
                else:
                    categories[cat][bool] = False

        if rule['detection']['condition']:
            conditions = list()
            condition_bools = list()
            cond_split = rule['detection']['condition'].split(' ')
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

        final_condition_bools = {}
        for condition in conditions:
            if condition['category'] in categories.keys():
                nb_true = 0
                for dict in categories[condition['category']].keys():
                    # print(dict, categories[condition['category']][dict])
                    if categories[condition['category']][dict]:
                        nb_true += 1

                final_condition_bools[condition['cid']] = {}
                if condition['threshold'] == 'none' or condition['threshold'] == 0:
                    if nb_true == 0:
                        final_condition_bools[condition['cid']]['bool'] = True
                    else:
                        final_condition_bools[cid]['bool'] = False
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
            final_condition = "{} {} {}".format(final_condition_bools[cb['a']]['bool'], cb['bool'], final_condition_bools[cb['b']]['bool'])
            if eval(final_condition):
                final_conditions.append('True')
            else:
                final_conditions.append('False')

        end_condition = ' and '.join(final_conditions)
        end_condition_bool = eval(end_condition)
        matches = list()
        if end_condition_bool:
            print('\nMatch found!\n')
            for key in final_condition_bools.keys():
                if final_condition_bools[key]:
                    for condition in conditions:
                        if condition['cid'] == key:
                            for key in categories[condition['category']].keys():
                                if categories[condition['category']][key]:
                                    print(condition['category'], ':', key)
                                    matches.append({'category' : condition['category'], 'string' : key})
        else:
            print('No match found.')
        return {'hit' : end_condition_bool, 'matches' : matches}


if __name__ == '__main__':
    star = STAR()
    rule = star.read_rule('rules/test.yml')
    if rule:
        hit =  star.scan_tweet(tweet, rule)
        print(hit)
