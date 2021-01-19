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

def toot(status, header, instance):
    t_data = dict()
    t_data['status'] = status
    t_data['visibility'] = 'unlisted'
    requests.post(instance + '/api/v1/statuses', headers = header, data = t_data)

def RTcheck(status):
    if 'retweeted_status' in status:
        return True
    else:
        return False
        # raise KeyError

def findLink(status):
    link = status.find('http')
    if link == 0 or link == 1:
        return -1
    elif link >= 2:
        linkIndex = status.rfind('https:')
        return linkIndex

def findColon(status):
    index = status.text.find(':')
    return index

def parse_and_toot(status):
    stat = status._json
    if stat['is_quote_status'] is True:
        if RTcheck(stat):
            enter = findColon(status)
            linkNum = findLink(status.text)
            stat2 = status.text[:enter+1] + '\n' + status.text[enter+2:linkNum] + '\n--\n' +'QUOTE @' + stat['quoted_status']['user']['screen_name'] + ':\n' + stat['quoted_status']['text']
            # stat2 = status.text + '\n--\n' + 'QUOTE @' + stat['retweeted_status']['quoted_status']['user']['screen_name'] + ':\n' + stat['retweeted_status']['quoted_status']['text']
            toot(stat2, header, instance)
        else:
            # enter = findColon(status)
            # stat2 = status.text[:enter+1] + '\n' + status.text[enter+2:] + '\n--\n' + 'QUOTE @' + stat['quoted_status']['user']['screen_name'] + ':\n' + stat['quoted_status']['text']
            stat2 = status.text + '\n--\n' + 'QUOTE @' + stat['quoted_status']['user']['screen_name'] + ':\n' + stat['quoted_status']['text']
            toot(stat2, header, instance)
    else:
        if RTcheck(stat):
            enter = findColon(status)
            stat2 = status.text[0:enter+1] + '\n' + status.text[enter+2:]
            linkNum = findLink(stat2)
            try:
                if linkNum == -1:
                    toot(stat2, header, instance)
                else:
                    stat3 = stat2[:linkNum]  ###
                    toot(stat3, header, instance)
            except:
                toot(stat2, header, instance)
        else:
            stat2 = status.text
            linkNum = findLink(stat2)
            try:
                if linkNum == -1:
                    toot(stat2, header, instance)
                else:
                    stat3 = stat2[:linkNum+1]  ###
                    toot(stat3, header, instance)
            except:
                toot(stat2, header, instance)

class streamListener(tweepy.StreamListener):
    def on_status(self, status):
        try:
            if status.id_str == user_id:
                parse_and_toot(status)
            else:
                return True
        except:
            toot('exception occured', header, instance)
    # def on_error(self, status_code):
    #     print(status_code)

if __name__ == '__main__':
    config.check_and_make()

    with open('config.json', 'r') as f:
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