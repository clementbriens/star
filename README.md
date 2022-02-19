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

### Detections

The following detections are available for building STAR rules. All of these detections are specified in the `utils/detections.py` file. All detections must appear under the `detection:` section of the file.

#### Strings

- `strings` : matches strings in the Tweet text
- `mentions` : matches mentioned users
- `urls` : matches URLs included in the tweet
- `user_name` : matches Tweet authors' username
- `screen_name` : matches Tweet authors'screen name
- `hashtags` : matches Tweet hashtags
- `description` : matches Tweet authors' account descriptions
- `lang` : matches Tweet language

You can also use Regex patterns surrounded by quotes on any of these fields by appending `re_` in front of these detections. For example, to use a regex pattern on usernames, you can use:

```
re_screen_name:
  - "[a-zA-Z]*[0-9]{8}"

```

#### Math

- `date` : Tweet date (YYYY/MM/DD)
- `account_date` : Author's account creation date (YYYY/MM/DD)
- `account_followers` : Number of author's followers
- `account_friends` : Number of author's friends
- `nb_mentions` : Number of users mentioned in tweets
- `tweets_per_day` : Average number of tweets per day by the author
- `tweets_per_week` : Average number of tweets per week by the author
- `sentiment_compound` : Overall tweet sentiment, between `-1` and `1`.
- `sentiment_negative` : Negative sentiment score, between `0` and `1`
- `sentiment_neutral` : Neutral sentiment score, between `0` and `1`
- `sentiment_positive` : Positive sentiment score, between `0` and `1`

In addition to specifying specific dates or numbers, you can also use ranges using `min`, `max`, `after` or `before`. Please refer to the following examples:

```
account_followers:
  - min 1000
  - max 5000
account_date:
  - before 2022/03/01
  - after 2022/01/01
```

#### Booleans

You can specify either `True` of `False` for each of these:

- `verified`
- `protected`
- `geo_enabled`
- `contributors_enabled`
- `is_translator`
- `is_translation_enabled`
- `profile_background_tile`
- `profile_use_background_image`
- `has_extended_profile`
- `default_profile`
- `default_profile_image`
- `profile_background_tile`
- `following`
- `follow_request_sent`
- `notifications`
- `is_quote_status`
- `favorited`
- `retweeted`
- `possibly_sensitive`
- `possibly_sensitive_appealable`

### Condition logic

Any detection added to the rule must be included in the condition logic. You can use the following booleans to build you condition:

- `all of strings` to detect if all `strings` match
- `3 of strings` to detect if 3 of the specified `strings` match
- `none of strings` to detect if none of the specified `strings` match
- `and`
- `or`


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
