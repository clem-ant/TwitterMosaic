import os
import requests
from PIL import Image
import twitter


################################################################
#                           CONFIGURATION
twitter_name = 'SamuelEtienne'
followers = True
following = False

api = twitter.Api(consumer_key='[replace here]',
                  consumer_secret='[replace here]',
                  access_token_key='[replace here]',
                  access_token_secret='[replace here]',
                  sleep_on_rate_limit=True)
################################################################


if not os.path.isdir(twitter_name):
    os.mkdir(twitter_name)


def download_img(screen_name, image_url, folder='.', ext='.jpg'):
    filename = folder+'/' + screen_name+ext
    r = requests.get(image_url, stream = True)
    if r.status_code == 200:
        Image.open(r.raw).convert('RGB').save(filename);
    else:
        print('Image download error :\'t', screen_name)

def get_user_pp(twitter_name):
    url = api.UsersLookup(screen_name=twitter_name)[0]._json['profile_image_url_https'].replace('_normal', '')
    download_img(twitter_name, url, ext='.png')



def get_all_follow(twitter_name, apicall, doneList = []):
    next_c = -1
    while(next_c != 0):
        print("Waiting for API... (rate limit)", end='\r')
        next_c, prev_c, data=apicall(screen_name=twitter_name, cursor=next_c, count=200)
        for user in data:
            userjson = user._json
            name = userjson['screen_name']
            if(name not in doneList):
                print("Download " + name + "               ", end='\r')
                download_img(name, userjson['profile_image_url_https'], folder=twitter_name)
                doneList.append(name)
    print("Done.                         ")
    return doneList



print("Downloading main pp....")
get_user_pp(twitter_name)

doneList = []
if(followers):
    print("Downloading followers...")
    doneList = get_all_follow(twitter_name, api.GetFollowersPaged)

if(following):
    print("Downloading following...")
    get_all_follow(twitter_name, api.GetFriendsPaged, doneList)
