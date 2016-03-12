import random
import re
import sys
import twitter
import markov
import pyttsx
import cPickle as pickle
import urllib

from htmlentitydefs import name2codepoint as n2c
from local_settings import *
from imgurpython import ImgurClient

# Edited for running direct on Ras Pi using cron
# Instead of giving up on a failed tweet retries until success
# Altered to bring in pre-prepared brain from disk

#    Read back brain generated by ingest.py

def connect():
    api = twitter.Api(consumer_key=MY_CONSUMER_KEY,
                          consumer_secret=MY_CONSUMER_SECRET,
                          access_token_key=MY_ACCESS_TOKEN_KEY,
                          access_token_secret=MY_ACCESS_TOKEN_SECRET)
    return api

def imgurconnect():

    imgur = ImgurClient(IMGUR_CLIENT_ID, IMGUR_CLIENT_SECRET)

    return imgur

def replytweetgen(mine, usernames, maxchar):                           
    success = False
    
    # this section does the actual building of reply tweet
    # changed it to try again on failure, default was to just give up

    while success == False:
            
        ebook_tweet = ""  # this clears out any previous unsuccessful attempt
        ebook_tweet_plain = ""
        
        # add users replying to
        for z in range(0,len(usernames)):
            if usernames[z]<>"MrPSB_ebooks": # don't reply to yourself you fucking idiot bot
                ebook_tweet += "@" + usernames[z] + " "

        ebook_tweet_plain = mine.generate_sentence()
        ebook_tweet += ebook_tweet_plain
                
        if ebook_tweet != None and len(ebook_tweet) < maxchar:
            success = True
                        
        elif ebook_tweet == None:
            print "I done goofed, there's nothing in the tweet"
            success = False
            
        elif len(ebook_tweet) >= maxchar:
            print "That's too long, whoopsypoops"
            success = False
            
        else:
            print "I have no idea what I'm doing"
            success = False
            
    return ebook_tweet, ebook_tweet_plain

if __name__=="__main__":

    # See if there's a lastmention stored, otherwise grab all you can

    spk = pyttsx.init()
    spk.setProperty('rate',100)
    spk.setProperty('voice','english_rp')
    spk.runAndWait()
    
    try:
        lastmention = pickle.load(open(BRAIN_LOCATION + "lastmention.p","rb"))
    except:
        lastmention = 0
    
    api = connect()
    mentions = api.GetMentions(since_id=lastmention)

    if len(mentions)>0:
        # Update saved lastmention
        lastmention = mentions[0].id
        pickle.dump(lastmention, open(BRAIN_LOCATION + "lastmention.p","wb"))

        # If there's something to reply to,
        # we'd best load the stuff to do that
        mine = pickle.load(open(BRAIN_LOCATION+ "botbrain.p" , "rb" ))
 
        for x in range(0,len(mentions)):

            # clear dict
            users = []

            #populate users
            users.append(mentions[x].user.screen_name)

            # enabling this in local_settings.py replies to all mentioned users as well
            # as user replying, high potential for abuse or spammyness
            # so use with care.  Probably needs a check for whether you follow/are followed by
    
            if REPLY_TO_ALL:
                for usr in range(0,len(mentions[x].user_mentions)):
                    users.append(mentions[x].user_mentions[usr].screen_name)

            reply = replytweetgen(mine, users, 120)

            if len(reply[0]) <= 60:

                print "OK IT'S TIME FOR A PICTURE!"
                print "Searching for: " + reply[1]
            
                imgur = imgurconnect()
                imgs = imgur.gallery_search('',{"q_any": reply[1]})

                print "Images found: " + str(len(imgs))
                
                if len(imgs) == 0:
                    print "No images found for search, going random"
                    imgs = imgur.gallery_random()
                
                for img in imgs:
                    if img.is_album == False and img.size < 5000000 and img.nsfw == False:
                        grabfile = urllib.URLopener()
                        print "Grabbing file " + img.link
                        imgfile = grabfile.retrieve(img.link)
                        break

                reply = api.PostMedia(reply[0],open(imgfile[0],"rb"),in_reply_to_status_id=mentions[x].id)
                
            else:
                reply = api.PostUpdate(reply[0],in_reply_to_status_id=mentions[x].id)
                 
            print "@" + mentions[x].user.screen_name.encode('UTF-8') + " said: " + mentions[x].text.encode('UTF-8')
            print "Replied: " + reply.text.encode('UTF-8')

            spk.say(reply.text.encode('UTF-8'))
            spk.runAndWait()
            
