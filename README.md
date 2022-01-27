# STAR- Simple Twitter Analysis Rules

These rules allow researchers to borrow the signature-based approach of YARA and Sigma rules to develop detection rules for tweets. Its applications can include detection of suspicious tweets from known datasets of tweets by state-sponsored actors, bot activity, and hate speech.

The rules are designed to be easily readable and writable as well as being compatible with the data outputted by the Twitter API.

## Writing a STAR Rule

STAR rules contain three main components:
* Metadata: any field to provide metadata for the rule, including a title, description, author etc.
* Detection: fields that are matched to the output of the Twitter API. Matches can include:
  * String matches
  * Math matches for dates, numerical values and more
  * Boolean matches
* Condition: add logic to your rule in order to determine the conditions by which this rule will report a tweet as a true positive

An example rule can be the following:

```
title: Russian IRA tweets
description: Detects tweets from the Russian Internet Research Agency
author: @clementbriens

detection:
  strings:
    - MAGA
    - Trump
  hashtags:
   - MAGA
   - ColumbiaChemicals
   account_date:
     - before 2014/01/01
     - after 2011/01/01
    followers:
    - min 10
    - max 5000
    verified : False
    default_profile_image : False

  condition: all of strings and 1 of hashtags and all of account_date and all of verified and all of default_profile_image
```

## Usage

`python star.py -r rule_path -i tweet_path -o output-path -f field1 field2`

### Arguments:

* `-r` / `--rule` : Path to the STAR rule to use to scan tweets

* `-i` / `--input` : Path to the tweet data to scan using the STAR rule. Currently accepts JSON files.

* `-o` / `--output` : Path and filename for the output. Currently accepted formats are JSON and CSV.

* `-f` / `--fields` : Custom fields to be returned in the output.

### Examples:

`python star.py -r rules/wwg1wga.yml -i tweets.json -o results.csv`

### Use STAR as a library

Alternatively, you can import STAR directly into your script and use its functions.

```
from star import STAR
import json

rule = star.read_rule('rules/wwg1wga.yml')
tweet = json.load(open('tweet.json'))

hit = star.scan_tweet(tweet, rule)
print(hit)
```
