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

Full documentation of these terms will be provided in the future.

## Usage

`python star.py -r rule_path -i tweet_path -o output-path -f field1 field2`

### Arguments:

* `-r` / `--rule` : Path to the STAR rule to use to scan tweets

* `-i` / `--input` : Path to the tweet data to scan using the STAR rule. Currently accepts JSON files.

* `-o` / `--output` : Path and filename for the output. Currently accepted formats are JSON and CSV.

* `-f` / `--fields` : Custom fields to be returned in the output.

### Examples:

`python star.py -r rules/wwg1wga.yml -i tweets.json -o results.csv`

## Use STAR as a library

Alternatively, you can import STAR directly into your script and use its functions.

```
from star import STAR
import json

rule = star.read_rule('rules/wwg1wga.yml')
tweet = json.load(open('tweet.json'))

hit = star.scan_tweet(tweet, rule)
print(hit)
```

## Using STAR to scan Tweets in real time

You can also use STAR to scan Tweets from the Twitter Stream API in real time.

### Configuration

Copy the `config.ini.sample` to a new `config.ini` file and fill in the fields with your Twitter API creds.

`cp config.ini.sample config.ini`

### Usage

To scan english-language Tweets from the Sampling API:

`python star_stream.py -m sample -l en -o json -p ./hits -r ./rules -v`

To scan Tweets mentioning specific keywords/terms:

`python star_stream.py -m filter -t Biden Trump -o json -p ./hits/us_hits -r ./rules/us_rules -v`

### Arguments

* `-m` / `--mode` : Select the streaming mode according to Twitter's API docs. Can be set to `sample` or `filter`

* `-l` / `--lang` : Language for stream sampling. Uses ISO-Alpha-2 country codes.

* `-t` / `--terms` : Keywords/terms for stream filtering.

* `-o` / `--output` : Output format. Defaults to `json`.

* `-p` / `--path` : Path for output.

* `-r` / `--rules` : Path for rules to scan. You can specify a specific folder with rules based on your analysis.

* `-v` / `--verbose` : Whether to output Tweet information for each hit to the CLI.
