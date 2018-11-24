import requests
import json
import indicoio
import operator

#jenny's api key for indicoio
indicoio.config.api_key = 'd3b7a4d2761c18a403b04e1fe7802e43'

moods = {}      # dict of users : dict of 5 moods avgs
counter = {}    # for incremental avgs of moods
last_post = -1 # keep track of analyzed post by date

# calculate incremental averages
def updateMood(user, feel, new_score):
    global moods
    curr_score = moods[user][feel]
    add_score = ((new_score - curr_score) / counter[user])
    moods[user][feel] += add_score

# parse through unanalyzed posts
def analyzePosts(user):
    global moods, counter, last_post
    profile = requests.get('https://api.vk.com/method/wall.get?owner_id=%s&access_token=30691f8630691f8630691f8607300e355a3306930691f866b917e8e8459c4931e49642f&v=5.92' %user).json()

    for each in profile['response']['items'][::-1]:
        # if post already analyzed, break
        if last_post >= each['date']:
            continue
        last_post = each['date']

        # get probabilities of emotions -> into list
        counter[user] += 1
        emotions = indicoio.emotion(each['text'])

        # update mood average
        for each in emotions:
            updateMood(user, each, emotions[each])

# obtain the mood with the highest confidence
# if all moods below 0.2, then neutral
def maxMood(user):
    max_mood = max(moods[user].items(), key=operator.itemgetter(1))[0]
    if moods[user][max_mood] < 0.2:
        return "neutral"
    return max_mood

# check the mood of the user
def checkMood(user):
    global moods, counter

    # add user if they're not in database
    if user not in counter:
        counter[user] = 0
        moods[user] = {'joy': 0, 'surprise': 0, 'anger': 0, 'fear': 0, 'sadness': 0}

    # classify emotions
    analyzePosts(user)

    # print(moods)
    return maxMood(user)

# execute
#print(checkMood(518274967))
