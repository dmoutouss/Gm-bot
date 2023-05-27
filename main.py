import requests
import os
import re
import schedule
import time
from datetime import datetime, timezone, timedelta

BEARER_TOKEN = 'YOUR_BEARER_TOKEN'

headers = {
    'Authorization': f'Bearer {BEARER_TOKEN}',
    'User-Agent': 'v2RecentSearchPython',
}

def count_gm_variations(text):
    gm_variations = ['gm', 'good morning', 'gud morning', 'GM']
    count = 0
    for variation in gm_variations:
        count += len(re.findall(r'\b{}\b'.format(variation), text, re.IGNORECASE))
    return count

def count_gm_tweets():
    gm_count = 0
    today = datetime.utcnow().date()
    midnight = datetime(today.year, today.month, today.day, tzinfo=timezone.utc)

    user_id = get_user_id('novordsem')
    following_ids = get_following_ids(user_id)

    for user_id in following_ids:
        user_timeline = get_user_tweets(user_id)
        for tweet in user_timeline:
            created_at = datetime.fromisoformat(tweet['created_at'][:-1]).replace(tzinfo=timezone.utc)
            if created_at >= midnight:
                gm_count += count_gm_variations(tweet['text'])
            else:
                break

    return gm_count

def get_user_id(username):
    url = f'https://api.twitter.com/2/users/by?usernames={username}'
    response = requests.get(url, headers=headers)
    data = response.json()
    return data['data'][0]['id']

def get_following_ids(user_id):
    url = f'https://api.twitter.com/2/users/{user_id}/following'
    response = requests.get(url, headers=headers)
    data = response.json()
    return [user['id'] for user in data['data']]

def get_user_tweets(user_id):
    url = f'https://api.twitter.com/2/users/{user_id}/tweets'
    response = requests.get(url, headers=headers)
    data = response.json()
    return data['data']

def job():
    gm_count = count_gm_tweets()
    print(f'Good morning tweets count: {gm_count}')

schedule.every(1).seconds.do(job)

while True:
    schedule.run_pending()
    time.sleep(1)
