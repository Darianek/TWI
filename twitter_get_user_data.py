from twitter_client import get_twitter_client
import math
from collections import Counter
import pymongo
import tweepy

'''
Connection with MongoDB
users_collection - contains details about users
graph_collection - contains already created graphs
'''
myclient = pymongo.MongoClient('localhost', 27017)
mydb = myclient["twitterAnalyzer"]
users_collection = mydb["users"]
graph_collection = mydb["graphs"]

# due to Twitter API limitations, max followers and friends for a given user
# is set to 1500
MAX_FRIENDS = 1500

def paginate(items, n):
    for i in range(0, len(items), n):
        yield items[i:i+n]

'''
Sorting user details before inserting to database
account - Twitter API user object
'''        
def get_user_details(account):  
    if account.protected:
        users_data = {"_id": account.screen_name,
                  "User id": account.id_str,
                  "Followers Count": str(0),
                  "Friends Count": str(account.friends_count),
                  "Created at": str(account.created_at),
                  "Protected": account.protected,
                  "Location": str(0),
                  "Verified": account.verified,
                  "Listed count": str(account.listed_count),
                  "Favourites count": str(account.favourites_count),
                  "Status count": str(account.statuses_count),
                  "Default profile": account.default_profile,
                  "Default profile image": account.default_profile_image}
    else:
        if account.location:
            location = account.location
        else:
            location = str(0)
            
        users_data = {"_id": account.screen_name,
                  "User id": account.id_str,
                  "Followers Count": str(account.followers_count),
                  "Friends Count": str(account.friends_count),
                  "Created at": str(account.created_at),
                  "Protected": account.protected,
                  "Location": location,
                  "Verified": account.verified,
                  "Listed count": str(account.listed_count),
                  "Favourites count": str(account.favourites_count),
                  "Status count": str(account.statuses_count),
                  "Default profile": account.default_profile,
                  "Default profile image": account.default_profile_image}

    return users_data

'''
Get number of tweets for given user from 2021
account - Twitter API user object
client - connection with Twitter API
'''
def get_user_tweets_number(account, client):
        counter = 0
        tweets = []
        if not account.protected:
            for page in tweepy.Cursor(client.user_timeline, screen_name=account.screen_name, count=200).pages(16):
                for status in page:
                    if str(status.created_at.year) == str(2021):
                        tweets.append(status.created_at.day)
                        counter += 1

        # calculating average tweets per day and hour
        b = Counter(sorted(tweets))
        all_tweets = 0
        for day in b:
            all_tweets += b[day]
        if len(b) == 0:
            average_per_day = 0
            average_per_hour = 0
        else:
            average_per_day = round(all_tweets/len(b), 2)
            average_per_hour = round(average_per_day/24, 2)

        return average_per_day, average_per_hour
    
'''
Get access file with keys to access Twitter API
safety - current file
'''
def get_access_file(safety):
    access_files = ['access/access1.txt', 'access/access2.txt', 'access/access3.txt', 'access/access4.txt', 'access/access5.txt',
              'access/access6.txt', 'access/access7.txt', 'access/access8.txt', 'access/access9.txt', 'access/access10.txt']
    if safety == 9:
        safety = 0
    else:
        safety += 1
    access_file = access_files[safety]
    return access_file, safety

'''
Download list of friends and followers of given user
account - Twitter API user object
client - connection with Twitter API
'''    
def get_user_connections(account, client):
    max_pages = math.ceil(MAX_FRIENDS / 5000)
    all_followers = []
    all_friends = []
        
    if not account.protected:
        for followers in tweepy.Cursor(client.followers_ids, screen_name=account.screen_name, count=1500).pages(max_pages):
            for chunk in paginate(followers, 100):
                users = client.lookup_users(user_ids=chunk)
                for user in users:
                    all_followers.append(user.screen_name)
                    
        for friends in tweepy.Cursor(client.friends_ids, screen_name=account.screen_name, count=1500).pages(max_pages):
            for chunk in paginate(friends, 100):
                users = client.lookup_users(user_ids=chunk)
                for user in users:
                    all_friends.append(user.screen_name)
    return list(all_followers), list(all_friends)

'''
Creating connections between users
screen_name - main user of the graph
deepth - deepth of graph
'''
def create_graph(screen_name, deepth):
    # safety parameter to changing credentials files
    safety = 0
    # getting access file
    access_file, safety = get_access_file(safety)
    # creating connection with Twitter API
    client = get_twitter_client(access_file)
    # add graph if not in database
    if not graph_collection.find_one({"_id": screen_name}):
        graph_collection.insert_one({"_id": screen_name, "Deepth": deepth})
    # list for users to check
    to_do = []
    to_do.append(screen_name)
    # loop for graph deepth   
    counter = 1
    # set to keep connections
    edges = set()
    for i in range(1, deepth+1):
        # loop for all users
        for name in set(to_do):
            if counter % 50 == 0:
                print(str(counter) + " DONE")
            counter += 1
            account = client.get_user(name)
            # check if friend and followers already available
            try:
                users_collection.find_one({"_id": name})['Friends']
            # if not availavle, download it
            except (KeyError, TypeError) as e:
                if str(e) == "'NoneType' object is not subscriptable":
                    users_collection.insert_one({"_id": name})
                    # list for users for current depth
                    temp = []
                    # check friends and followers of given user
                    try:
                        followers, friends = get_user_connections(account, client)
                        for follower in followers:
                            record = follower + "," + name + ",Directed"
                            # save sonnection
                            edges.add(record)
                            my_query = {"_id": screen_name}
                            data = {"$addToSet": {"Edges": record}}
                            graph_collection.update_one(my_query, data)
                        for friend in friends:
                            record = name + "," + friend + ",Directed"
                            # save connection
                            edges.add(record)
                            my_query = {"_id": screen_name}
                            data = {"$addToSet": {"Edges": record}}
                            graph_collection.update_one(my_query, data)
                        # add users to do for next deepth
                        temp += followers
                        temp += friends
                    except tweepy.TweepError as e:
                        # if Twitter API limit is reached, change access file
                        if e.response.text == '{"errors":[{"message":"Rate limit exceeded","code":88}]}':
                            print('CHANGING ACCESS FILE TO ' + str(safety) + '!')
                            access_file, safety = get_access_file(safety)
                            # try to check friends and followers of given user again
                            # with new access file
                            try:
                                client = get_twitter_client(access_file)
                                account = client.get_user(screen_name)
                                followers, friends = get_user_connections(account, client)
                                # check friends and followers of given user
                                for follower in followers:
                                    record = follower + "," + name + ",Directed"
                                    # save connection
                                    edges.add(record)
                                    my_query = {"_id": screen_name}
                                    data = {"$addToSet": {"Edges": record}}
                                    graph_collection.update_one(my_query, data)
                                for friend in friends:
                                    record = name + "," + friend + ",Directed"
                                    # save connection
                                    edges.add(record)
                                    my_query = {"_id": screen_name}
                                    data = {"$addToSet": {"Edges": record}}
                                    graph_collection.update_one(my_query, data)
                                # add users to do for next deepth
                                temp += followers
                                temp += friends
                            except tweepy.TweepError:
                                pass
                        # otherwise, probably deleted user was found
                        else:
                            pass
                elif str(e) == "'Friends'":               
                    # list for users for current depth
                    temp = []
                    # check friends and followers of given user
                    try:
                        followers, friends = get_user_connections(account, client)
                        for follower in followers:
                            record = follower + "," + name + ",Directed"
                            # save connection
                            edges.add(record)
                            my_query = {"_id": screen_name}
                            data = {"$addToSet": {"Edges": record}}
                            graph_collection.update_one(my_query, data)
                        for friend in friends:
                            record = name + "," + friend + ",Directed"
                            # save connection
                            edges.add(record)
                            my_query = {"_id": screen_name}
                            data = {"$addToSet": {"Edges": record}}
                            graph_collection.update_one(my_query, data)
                        # add users to do for next deepth
                        temp += followers
                        temp += friends
                    except tweepy.TweepError as e:
                        # if Twitter API limit is reached, change access file
                        if e.response.text == '{"errors":[{"message":"Rate limit exceeded","code":88}]}':
                            print('CHANGING ACCESS FILE TO ' + str(safety) + '!')
                            access_file, safety = get_access_file(safety)
                            # try to check friends and followers of given user again
                            # with new access file
                            try:
                                client = get_twitter_client(access_file)
                                account = client.get_user(screen_name)
                                followers, friends = get_user_connections(account, client)
                                for follower in followers:
                                    record = follower + "," + name + ",Directed"
                                    # save connection
                                    edges.add(record)
                                    my_query = {"_id": screen_name}
                                    data = {"$addToSet": {"Edges": record}}
                                    graph_collection.update_one(my_query, data)
                                for friend in friends:
                                    record = name + "," + friend + ",Directed"
                                    # save connection
                                    edges.add(record)
                                    my_query = {"_id": screen_name}
                                    data = {"$addToSet": {"Edges": record}}
                                    graph_collection.update_one(my_query, data)
                                temp += followers
                                temp += friends
                            except tweepy.TweepError:
                                pass
                        # otherwise, probably deleted user was found
                        else:
                            pass
        if i == 1:
            to_do.remove(screen_name)
        to_do += temp
        
        # save connections to file
        filename = 'connections/{}.csv'.format(screen_name)
        with open(filename, 'w') as f:
            for edge in list(edges):
                f.write(edge + '\n')

'''
Download details of single user
screen_name - username
'''
def get_single_user(screen_name):

    # safety parameter to changing credentials files
    safety = 0
    # getting access file
    access_file, safety = get_access_file(safety)
    # creating connection with Twitter API
    client = get_twitter_client(access_file)
    try:
        # if user details already exists in database get them
        users_collection.find_one({"_id": screen_name})['Verified']
        user_details = users_collection.find_one({"_id": screen_name})
    except:      
        # otherwise download user details
        account = client.get_user(screen_name)
        user_details = get_user_details(account)
        average_per_day, average_per_hour = get_user_tweets_number(account, client)
        user_details['Tweets per day'] = average_per_day
        user_details['Tweets per hour'] = average_per_hour
        query = {"_id": screen_name}
        # if users exists in database but without details
        # append details
        if users_collection.find_one({"_id": screen_name}):
            values = {"$set": user_details}
            users_collection.update_one(query, values)
        # otherwise insert new user
        else:
            users_collection.insert_one(user_details)         
    return user_details

'''
Download details for list of users
users - list of users
'''
def get_users_data(users):
    # safety parameter to changing credentials files
    safety = 0
    # getting access file
    access_file, safety = get_access_file(safety)
    # creating connection with Twitter API
    client = get_twitter_client(access_file)
    counter = 0
    for user in users:
        if counter % 50 == 0:
            print(str(counter) + " DONE")
        counter += 1
        try:
            # if user details already exists in database skip user
            users_collection.find_one({"_id": user})['Followers Count']
        except:
            #otherwise try to download them
            try:
                account = client.get_user(user)
                user_details = get_user_details(account)
                average_per_day, average_per_hour = get_user_tweets_number(account, client)
                user_details['Tweets per day'] = average_per_day
                user_details['Tweets per hour'] = average_per_hour
                query = {"_id": user}
                # if users exists in database but without details
                # append details
                if users_collection.find_one({"_id": user}):
                    values = {"$set": user_details}
                    users_collection.update_one(query, values)
                # otherwise insert new user
                else:
                    users_collection.insert_one(user_details)
            except tweepy.TweepError as e:
                # if Twitter API limit is reached, change access file
                if e.response.text == '{"errors":[{"message":"Rate limit exceeded","code":88}]}':
                    print(e.response.text)
                    print('CHANGING ACCESS FILE TO ' + str(safety) + '!')
                    access_file, safety = get_access_file(safety)
                    client = get_twitter_client(access_file)
                    # try to download with new access file
                    try:
                        user_details = get_user_details(account)
                        average_per_day, average_per_hour = get_user_tweets_number(account, client)
                        user_details['Tweets per day'] = average_per_day
                        user_details['Tweets per hour'] = average_per_hour
                        query = {"_id": user}
                        # if users exists in database but without details
                        # append details
                        if users_collection.find_one({"_id": user}):
                            values = {"$set": user_details}
                            users_collection.update_one(query, values)
                        # otherwise insert new user
                        else:
                            users_collection.insert_one(user_details)
                    except tweepy.TweepError:
                        pass