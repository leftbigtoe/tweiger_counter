# -*- coding: utf-8 -*-
"""
Created on Sat May 25 20:46:25 2013

@author: leftbigtoe
@author: dadarakt
"""

from tweepy import StreamListener
import tweepy, time, json
from thread import start_new_thread
import numpy as np
import serial
import sys
import platform

class SListener(StreamListener):

    def __init__(self, api = None, max = 180):

        # internal parameters        
        self.nBins              = 60
        self.maxWPM             = float(max)
        self.available_degrees  = 180.0
        self.CLICK              = 200
        self.api                = api or API()

        # intialize variables
        self.counter            = 0
        self.buffer             = np.zeros(self.nBins, dtype = int)
        self.wpm                = 0

        # try to automatically set the port, make manual changes if necessary
        os = platform.system()
        if (os == "Windows"):
          port_name = "COM4"
        elif(os == "Linux"): 
          port_name = "/dev/ttyACM0"
        else:
          print "You are assumingly not using linux or windows: Please go to \
          the file and set your port manually."
          sys.exit()

        # open arduino connection
        self.ardu = serial.Serial(port_name, 9600, timeout = 3)
        # start buffer manager in seperate thread
        start_new_thread(self.bufferManager,())
        
    def bufferManager(self):
        """
        busy waiting thread that sums up received keywords in one second
        writes it to the buffer every second to the buffer, calculates the
        average and pushes that to the arduino
        """
        # intialize index to current processor time
        index = int(time.time()%self.nBins)            
  # open arduino connection
        while(True):
            time.sleep(0.1)
            curr_time = int(time.time()%self.nBins)
            # if new bin is entered
            if (not(index == curr_time)): 
                # fill count of last second in buffer
                self.wpm           += self.counter - self.buffer[index]
                self.buffer[index]  = self.counter
                # increment index to next bin
                index = curr_time  
                # reset counter
                self.counter = 0
                # push to arduino
                start_new_thread(self.arduPusherWPM,())

    def on_data(self, status):
        """ everytime a tweet comes in, counter is incremented """
        self.counter += 1
        start_new_thread(self.arduPusherClick,(1,))
        # start new thread to print out the text
        start_new_thread(self.printerTweet, (status,))
        return   
        
    def printerTweet(self, tweet):
        """ loads tweet as json and prints text to command line """
        #print tweet  
        try:
            text = json.loads(tweet)["text"]
            print text.encode('cp850', errors='replace') + '\n'
        except:
            print 'could not get text of tweet'
    
    def arduPusherWPM(self):
        """ 
        pushes current wpm/maxWPM-ratio to the arduino, 
        mapped to 180 degrees 
        """
        tmp = (self.wpm / self.maxWPM) * self.available_degrees \
              if self.wpm < self.maxWPM else self.available_degrees
        # send number as char        
        self.ardu.write(chr(int(tmp)))                        
        
    def arduPusherClick(self, dummy = 0):
        """ pushes signal a click signal to the arduino """
        self.ardu.write(chr(self.CLICK))
        
    def reset(self):
        """ resets the counter and the buffer to start with new word """
        self.buffer   = np.zeros(self.nBins)
        self.counter  = 0
        

def main():

    # load consumer token & secret key from the file "auth.txt"
    f = open('auth.txt','r')
    c_token, c_secret, a_token, a_secret = (line.strip() for line in f)
    f.close()
    
    # create OAuth handler and get access
    my_auth = tweepy.OAuthHandler(c_token, c_secret)
    my_auth.set_access_token(a_token, a_secret)
         
    # set up listener
    api      = tweepy.API(my_auth)
    # Test if authentication worked
    if api.verify_credentials:
      print "--- Authentication successfull"
    else:
      print "-!- Authentication failed"

    # Check if there is a numeral as an argument which is then used as maxWPM
    tmp = 180
    for arg in sys.argv[1:]:
      if arg.isdigit():
        tmp = int(arg)

    # Set-up listener
    my_listener = SListener(api, max = tmp)
    
    # Filter stream for given words
    filterWords = [x for x in sys.argv[1:] if not(x.isdigit())]

    try:    
        stream = tweepy.Stream(auth = my_auth, listener = my_listener)    
        print "--- Filtering Tweets for"
        for word in filterWords:
            print "  - " + word
        print "--- Here are the tweets: \n"
        stream.filter(track = filterWords)
    except KeyboardInterrupt:
        stream.disconnect()
        "--- Shutting down, stay safe"
    except:
        print "-!- Could not establish connection"
        stream.disconnect()
    
if __name__ == '__main__':

  # catch invalid use
  if(len(sys.argv) <= 1):
    print "no command line arguments used, using default"
    sys.argv = ['', 'nuclear', 'atomic energy', 'nuclear radiation']

  main()
