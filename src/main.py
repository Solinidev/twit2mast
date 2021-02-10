import os
import sys
import json
import traceback, logging
import config
try:
    import tweepy
except:
    sys.exit("tweepy is not installed.")
try:
    import requests
except:
    sys.exit("requests is not installed.")

def setHeader(token):
    header = {'Authorization' : 'Bearer ' + token}
    return header

def upload_media(link, header, instance):
    media = requests.get(link).content
    files = {'file' : media}
    r = requests.post(instance + '/api/v1/media', headers = header, files = files)
    if r.status_code == 200:
        return r.json()['id']
    else:
        return False

def toot(status, header, instance):
    t_data = dict()
    t_data['status'] = status
    t_data['visibility'] = 'unlisted'
    requests.post(instance + '/api/v1/statuses', headers = header, data = t_data)

def toot_with_media(status, header, instance, media):
    t_data = dict()
    t_data['status'] = status
    t_data['visibility'] = 'unlisted'
    t_data['media_ids[]'] = media
    requests.post(instance + '/api/v1/statuses', headers = header, data = t_data)

def RTcheck(status):
    if 'retweeted_status' in status:
        return True
    else:
        return False

def replyCheck(status, userid):
    reply = status['in_reply_to_user_id_str']
    if reply == userid:
        return False
    elif reply is None:
        return False
    else:
        return True

def truncCheck(status, onrt):
    if onrt is True:
        if status['retweeted_status']['truncated'] is True:
            return True
        else:
            return False
    else:
        if status['truncated'] is True:
            return True
        else:
            return False

def get_full(status, onrt):
    if onrt is True:
        return status['retweeted_status']['extended_tweet']['full_text']
    else:
        return status['extended_tweet']['full_text']

def findColon(status):
    return status.text.find(':')

def findColon_str(string):
    return string.find(':')

def mediaCheck(status):
    # 진짜 개오바임 방법 찾아서 꼭 수정하기
    if 'extended_entities' in status:
        return 1
    try:
        if status['extended_tweet']['extended_entities']:
            return 2
    except KeyError:
        try:
            if status['quoted_status']['extended_tweet']['extended_entities']:
                return 3
        except KeyError:
            try:
                if status['retweeted_status']['extended_tweet']['extended_entities']:
                    return 4
            except:
                return False

def media_type(media):
    return media['type']

def getLinks(status, switch):
    if switch == 1:
        media = status['extended_entities']['media']
    elif switch == 2:
        media = status['extended_tweet']['extended_entities']['media']
    elif switch == 3:
        media = status['quoted_status']['extended_tweet']['extended_entities']['media']
    elif switch == 4:
        media = status['retweeted_status']['extended_tweet']['extended_entities']['media']
    linkList = []
    for link in media:
        mtype = media_type(link)
        if mtype == 'photo':
            linkList.append(link['media_url_https'])
        elif mtype == 'animated_gif' or mtype == 'video':
            linkList.append(link['video_info']['variants'][0]['url'])
    return linkList

def make_status(stat, stat2):
    midi = mediaCheck(stat)
    if midi:
        links = getLinks(stat, midi)
        mediaIds = []
        for link in links:
            mediaId = upload_media(link, header, instance)
            if mediaId:
                mediaIds.append(mediaId)
        toot_with_media(stat2, header, instance, mediaIds)
    else:
        toot(stat2, header, instance)

def parse_and_toot(status, userid):
    stat = status._json
    if stat['is_quote_status'] is True:
        if RTcheck(stat):
            if truncCheck(stat, True) is True:
                if stat['quoted_status']['truncated'] is True:
                    msg = get_full(stat, True)
                    msg2 = 'RT @' + stat['retweeted_status']['user']['screen_name'] + ':\n' + msg + '\n--\n' + 'QUOTE @' + stat['quoted_status']['user']['screen_name'] + ':\n' + stat['quoted_status']['extended_tweet']['full_text']
                    make_status(stat, msg2)
                else:
                    msg = get_full(stat, True)
                    msg2 = 'RT @' + stat['retweeted_status']['user']['screen_name'] + ':\n' + msg + '\n--\n' + 'QUOTE @' + stat['quoted_status']['user']['screen_name'] + ':\n' + stat['quoted_status']['text']
                    make_status(stat, msg2)
            else:
                if stat['quoted_status']['truncated'] is True:
                    enter = findColon(status)
                    msg = status.text[:enter+1] + '\n' + status.text[enter+2:] + '\n--\n' + 'QUOTE @' + stat['quoted_status']['user']['screen_name'] + ':\n' + stat['quoted_status']['extended_tweet']['full_text']
                    make_status(stat, msg)
                else:
                    enter = findColon(status)
                    stat2 = status.text[:enter+1] + '\n' + status.text[enter+2:] + '\n--\n' + 'QUOTE @' + stat['quoted_status']['user']['screen_name'] + ':\n' + stat['quoted_status']['text']
                    make_status(stat, stat2)
        else:
            if truncCheck(stat, False) is True:
                if stat['quoted_status']['truncated'] is True:
                    msg = get_full(stat, False)
                    msg2 = msg + '\n--\n' + 'QUOTE @' + stat['quoted_status']['user']['screen_name'] + ':\n' + stat['quoted_status']['extended_tweet']['full_text']
                    make_status(stat, msg2)
                else:
                    msg = get_full(stat, False)
                    msg2 = msg + '\n--\n' + 'QUOTE @' + stat['quoted_status']['user']['screen_name'] + ':\n' + stat['quoted_status']['text']
                    make_status(stat, msg2)
            else:
                if stat['quoted_status']['truncated'] is True:
                    msg = status.text + '\n--\n' + 'QUOTE @' + stat['quoted_status']['user']['screen_name'] + ':\n' + stat['quoted_status']['extended_tweet']['full_text']
                    make_status(stat, msg)
                else:
                    stat2 = status.text + '\n--\n' + 'QUOTE @' + stat['quoted_status']['user']['screen_name'] + ':\n' + stat['quoted_status']['text']
                    make_status(stat, stat2)
    elif replyCheck(stat, userid):
        return True
    else:
        if RTcheck(stat):
            if truncCheck(stat, True) is True:
                msg = get_full(stat, True)
                enter = findColon_str(msg)
                msg2 = 'RT @' + stat['retweeted_status']['user']['screen_name'] + ':\n' + msg[:enter+1] + '\n' + msg[enter+2:]
                make_status(stat, msg2)
            else:
                enter = findColon(status)
                stat2 = status.text[0:enter+1] + '\n' + status.text[enter+2:]
                make_status(stat, stat2)
        else:
            if truncCheck(stat, False) is True:
                msg = get_full(stat, False)
                make_status(stat, msg)
            else:
                msg = stat['text']
                make_status(stat, msg)

class streamListener(tweepy.StreamListener):
    def on_status(self, status):
        try:
            stat = status._json
            userID = stat['user']['id_str']
            if user_id == userID:
                parse_and_toot(status, userID)
            else:
                return True
        except:
            toot('exception occured', header, instance)
            with open(os.path.join(par, 'error.txt'), 'a') as log:
                log.write(traceback.format_exc() + '\n\n')

if __name__ == '__main__':
    logging.basicConfig(level=logging.ERROR)

    path = os.path.dirname(os.path.abspath(__file__))
    par = os.path.join(path, os.pardir)

    config.check_and_make(par)

    with open(os.path.join(par, 'config.json'), 'r') as f:
        data = json.load(f)

        consumer_key = data["twitter"]["api_keys"]["consumer_key"]
        consumer_secret = data["twitter"]["api_keys"]["consumer_secret"]
        access_token = data["twitter"]["api_keys"]["access_token"]
        access_secret = data["twitter"]["api_keys"]["access_secret"]
        user_id = data["twitter"]["id"]

        mastodon_access = data["mastodon"]["access_token"]
        instance = data["mastodon"]["instance"]

    header = setHeader(mastodon_access)

    while True:
        try:
            auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
            auth.set_access_token(access_token, access_secret)


            userStreamListener = streamListener()
            userStream = tweepy.Stream(auth = auth, listener = userStreamListener)

            print('Stream connected')
            userStream.filter(follow=[user_id])
        except:
            print('Stream reconnecting . . .')
            continue