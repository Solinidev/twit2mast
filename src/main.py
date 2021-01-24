import os
import sys
import json
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
    return r.json()['id']

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

def findColon(status):
    index = status.text.find(':')
    return index

def mediaCheck(status):
    if 'extended_entities' in status:
        return True
    else:
        return False

def media_type(media):
    mtype = media['type']
    return mtype

def getLinks(status):
    media = status['extended_entities']['media']
    linkList = []
    for link in media:
        mtype = media_type(link)
        if mtype == 'photo':
            linkList.append(link['media_url_https'])
        elif mtype == 'animated_gif' or mtype == 'video':
            linkList.append(link['video_info']['variants'][0]['url'])
    return linkList

def make_status(stat, stat2):
    if mediaCheck(stat):
        links = getLinks(stat)
        mediaIds = []
        for link in links:
            mediaId = upload_media(link, header, instance)
            mediaIds.append(mediaId)
        toot_with_media(stat2, header, instance, mediaIds)
    else:
        toot(stat2, header, instance)

def parse_and_toot(status, userid):
    stat = status._json
    # print(stat)
    if stat['is_quote_status'] is True:
        if RTcheck(stat):
            enter = findColon(status)
            stat2 = status.text[:enter+1] + '\n' + status.text[enter+2:] + '\n--\n' +'QUOTE @' + stat['quoted_status']['user']['screen_name'] + ':\n' + stat['quoted_status']['text']
            make_status(stat, stat2)
        else:
            stat2 = status.text + '\n--\n' + 'QUOTE @' + stat['quoted_status']['user']['screen_name'] + ':\n' + stat['quoted_status']['text']
            make_status(stat, stat2)
    elif replyCheck(stat, userid):
        return True
    else:
        if RTcheck(stat):
            enter = findColon(status)
            stat2 = status.text[0:enter+1] + '\n' + status.text[enter+2:]
            make_status(stat, stat2)
        else:
            stat2 = status.text
            make_status(stat, stat2)

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
    # def on_error(self, status_code):
    #     print(status_code)

if __name__ == '__main__':
    path = os.path.dirname(os.path.abspath(__file__))
    par = os.path.join(path, os.pardir)

    config.check_and_make(par)

    with open(par + '/config.json', 'r') as f:
        data = json.load(f)

        consumer_key = data["twitter"]["api_keys"]["consumer_key"]
        consumer_secret = data["twitter"]["api_keys"]["consumer_secret"]
        access_token = data["twitter"]["api_keys"]["access_token"]
        access_secret = data["twitter"]["api_keys"]["access_secret"]
        user_id = data["twitter"]["id"]

        mastodon_access = data["mastodon"]["access_token"]

    header = setHeader(mastodon_access)
    instance = 'https://twingyeo.kr'

    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_secret)


    userStreamListener = streamListener()
    userStream = tweepy.Stream(auth = auth, listener = userStreamListener)

    userStream.filter(follow=[user_id])