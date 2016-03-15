# mrpsb_ebooks

Originally based on [tommeagher's](https://github.com/tommeagher) Python port of [@harrisj's](https://twitter.com/harrisj) [iron_ebooks](https://github.com/harrisj/iron_ebooks/) Ruby script. 
I've adapted it to run on my Raspberry Pi by having cron call it, and picking up tweets from a text file built from a twitter archive dump instead of live from Twitter

Currently used for [@MrPSB_ebooks](https://twitter.com/mrpsb_ebooks)

## Setup

1. Clone this repo
2. Create a Twitter account that you will post to.
3. Sign into https://dev.twitter.com/apps with the same login and create an application. Make sure that your application has read and write permissions to make POST requests.
4. Make a copy of the `local_settings_example.py` file and name it `local_settings.py`
5. Take the consumer key (and secret) and access token (and secret) from your Twiter application and paste them into the appropriate spots in `local_settings.py`.
6. If you want the bot to occasionally post images scraped from Imgur then get an Imgur Client ID and secret and put them in local_settings.py as well.  If you don't then probably comment out all the image posting stuff for now until I learn to code.
7. In `local_settings.py`, be sure to add the handle of the Twitter user you want your _ebooks account to be based on. To make your tweets go live, change the `DEBUG` variable to `False`.
7. Put a UTF-8 encoded text file of your tweets (or whatever), in the same directory as the script.  Point TEXT_SOURCE in `local_settings.py` at it, and run `ingest_2.py`.  This builds the SQLite DB.
8. Run speak-ebooks-pics.py whenever you want to spam twitter with a load of nonsense and have whatever you're using read them out in a hilarious TTS voice
9. The only Python requirement for this script is [python-twitter](https://github.com/bear/python-twitter) - this can be picked up using apt-get on raspian.
10. To use speech you will need pyttsx (pip install pyttsx) otherwise comment all that nasty stuff out, guy!
11. For pictures you will need imgurpython (pip install imgurpython) also yeah comment out if you don't need it.
12. Flood Twitter with your nonsense for no reason

## Configuring

There are several parameters that control the behavior of the bot. You can adjust them by setting them in your `local_settings.py` file. 

```
ODDS = 8
```

The bot does not run on every invocation. It runs in a pseudorandom fashion. At the beginning of each time the script fires, `guess = random.choice(range(ODDS))`. If `guess == 0`, then it proceeds. If your `ODDS = 8`, it should run one out of every 8 times, more or less. You can override it to make it more or less frequent. To make it run every time, you can set it to 0.
By default, the bot ignores any tweets with URLs in them because those might just be headlines for articles and not text you've written.

```
ORDER = 2
```

The ORDER variable should represent the Markov index, which is a measure of associativity in the generated Markov chains.  I think I've worked out the reason it breaks and have shoved it in comments in Markov_2.py but I've been too lazy to fix it as Order 2 seems fine.

## Debugging

If you want to test the script or to debug the tweet generation, you can skip the random number generation and not publish the resulting tweets to Twitter.

First, adjust the `DEBUG` variable in `local_settings.py`.

```
DEBUG = True 
```


## Credit
Method the bot uses is still very much based heavily This is very much a tweaked (with all the grace and skill of a man smashing things with a hammer) version of tommeagher's port of harrisj's work.  I've extended the Markov.py from that repo a bit to take care of using SQLite to try and speed up the Pi's access when it's got a large file to work with.  It's only moderately successful, but I had fun.

If it falls over, it's more than likely my fault, so probably best check the original repos I've forked this from and pick up some competent code!
