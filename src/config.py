import os
import json
from collections import OrderedDict

def check_and_make(path):
    if os.path.isfile(os.path.join(path, "config.json")):
        return
    else:
        consumer_key = input("Enter your Twitter API key(consumer key) : ").strip()
        consumer_secret = input("Enter your Twitter API secret key(consumer secret) : ").strip()
        access_token = input("Enter your Twitter access token : ").strip()
        access_secret = input("Enter your Twitter access token secret : ").strip()

        # screen_name = input("Enter Twitter username that you want to mirror : ")
        user_id = input("Enter user ID that you want to mirror (NOT username) : ").strip()

        mastodon_access = input("Enter your mastodon access token : ").strip()


        data = OrderedDict()

        data["twitter"] = {
            "api_keys" : {
                "consumer_key" : consumer_key,
                "consumer_secret" : consumer_secret,
                "access_token" : access_token,
                "access_secret" : access_secret
            },
            #"screen_name" : screen_name,
            "id" : user_id
        }

        data["mastodon"] = {
            "access_token" : mastodon_access
        }

        with open(os.path.join(path, 'config.json'), 'w', encoding="utf-8") as make_file:
            json.dump(data, make_file, ensure_ascii=False, indent="\t")

        print('Configuration saved into ' + path + ' as config.json')
        return

if __name__ == '__main__':
    path = os.path.dirname(os.path.abspath(__file__))
    parpath = os.path.join(path, os.pardir)

    check_and_make(parpath)