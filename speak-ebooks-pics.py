import random
import twitter
import markov
import pyttsx
import sys
import cPickle as pickle
import urllib

from local_settings import *
from imgurpython import ImgurClient

# Edited for running direct on Ras Pi using cron
# Instead of giving up on a failed tweet retries until success
# Altered to bring in pre-prepared brain from disk

try:
    if sys.argv[1] == "JFDI":
	ODDS = 1
except:
    pass

def connect():
    api = twitter.Api(consumer_key=MY_CONSUMER_KEY,
                          consumer_secret=MY_CONSUMER_SECRET,
                          access_token_key=MY_ACCESS_TOKEN_KEY,
                          access_token_secret=MY_ACCESS_TOKEN_SECRET)
    return api

def imgurconnect():

    imgur = ImgurClient(IMGUR_CLIENT_ID, IMGUR_CLIENT_SECRET)

    return imgur

if __name__=="__main__":
        
    if DEBUG==False:
        guess = random.choice(range(ODDS))
    else:
        guess = 0

    if guess == 0:
        if DEBUG == False:
            api = connect()
                           
        success = False
        imgtweet = False

        # Read back brain generated by ingest.py
        mine = pickle.load(open( BRAIN_LOCATION + "botbrain.p" , "rb" ))
        source_tweets = pickle.load(open( BRAIN_LOCATION + "source_tweets.p" , "rb" ))
        
        # this section does the actual building of tweet
        # changed it to try again on failure, default was to just give up

        while success == False:
            
            ebook_tweet = ""  # this clears out any previous unsuccessful attempt
            
            ebook_tweet = mine.generate_sentence()
   
            # if a tweet is very short, this uses it to search imgur with the
            # tweet as query and post the tweet with the image
            
            if ebook_tweet != None and len(ebook_tweet) < 40:
                print "I'm going to post a disgusting image: " + ebook_tweet

                # connect to imgur, search for an image, if you don't find
                # one then grab a random one
              
                imgur = imgurconnect()
                imgs = imgur.gallery_search('',{'q_any': ebook_tweet})

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
                        
                success = True
                imgtweet = True

            if imgtweet == False:
                #throw out tweets that match anything from the source account.
                if ebook_tweet != None and len(ebook_tweet) < 120:
                    success = True
                    for tweet in source_tweets:
                        if ebook_tweet[:-1] not in tweet:
                            continue
                        else: 
                            print "TOO SIMILAR: " + ebook_tweet
                            success = False
                            imgtweet = False
                elif ebook_tweet == None:
                    print "I done goofed, there's nothing in the tweet"
                    success = False
                elif len(ebook_tweet) >= 120:
                    print "That's too long, whoopsypoops"
                    success = False
                else:
                    print "I have no idea what I'm doing"
                    success = False
            
        # Couldn't find anything wrong with the tweet so here goes
            if success == True:
                if DEBUG == False:
                    if imgtweet == True:
                        status = api.PostMedia(ebook_tweet, open(imgfile[0],"r"))
                    else:
                        status = api.PostUpdate(ebook_tweet)
                        s = status.text.encode('utf-8')
                        print s
                        spk = pyttsx.init()
                        spk.setProperty('rate',100)
                        spk.setProperty('voice','english_rp')
                        spk.say(s)
                        spk.runAndWait()
                        
                else:
                    print "SUCCESS: " + ebook_tweet
                
    else:
        print "This time I'm not doing a tweet, so there" #message if the random number fails.
