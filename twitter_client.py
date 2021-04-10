from tweepy import API
from tweepy import OAuthHandler


def get_twitter_auth(access_file):

    with open(access_file) as f:
        data = f.readlines()

    consumer_key = data[0].rstrip()
    consumer_secret = data[1].rstrip()
    access_token = data[2].rstrip()
    access_secret = data[3].rstrip()

    auth = OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_secret)
    return auth


def get_twitter_client(access_file):

    auth = get_twitter_auth(access_file)
    client = API(auth)
    return client
