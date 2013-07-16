# -*- coding: utf-8 -*-
"""
Created on Sat May 25 20:46:25 2013

@author: leftbigtoe
"""

from tweepy import StreamListener
import tweepy, time, json
from thread import start_new_thread
import numpy as np
import serial

class SListener(StreamListener):

    def __init__(self, api = None):
        # internal parameters        
        self.nBins = 60
        self.maxWPM = 180
        self.CLICK = 200
        
        self.api = api or API()
        
        # intialize variables
        self.counter = 0
        self.buffer = np.zeros(60, dtype = int)
        self.wpm = 0

        # open arduino connection
        self.ardu = serial.Serial("COM4", 9600, timeout = 3)
        # start buffer manager in seperate thread
        start_new_thread(self.bufferManager,(0,))
        
    def bufferManager(self,dummy):
        """
        busy waiting thread that sums up received keywords in one second
        writes it to the buffer every second to the buffer, calculates the
        average and pushes that to the arduino
        """
        # intialize index
        index = int(time.clock()%60)         
        # endless loop        
  
        while(True):
            time.sleep(0.01)
            # if new bin is entered
            if (not(index == int(time.clock()%self.nBins))):
                # fill count of last second in buffer
                self.wpm += self.counter - self.buffer[index]
                self.buffer[index] = self.counter
                # increment index to next bin
                index = int(time.clock()%self.nBins)  
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
        """ pushes current wpm to the arduino """
        tmp = self.wpm if self.wpm < self.maxWPM else self.maxWPM
        # send number as char        
        self.ardu.write(chr(int(tmp)))                        
        
    def arduPusherClick(self, dummy = 0):
        """ pushes signal a click signal to the arduino """
        self.ardu.write(chr(self.CLICK))
        
    def reset(self):
        """ resets the counter and the buffer to start with new word """
        self.buffer = np.zeros(self.nBins)
        self.counter = 0
        

def main():

    # load consumer token & secret key
    f = open('auth.txt','r')
    c_token, c_secret, a_token, a_secret = (line.strip() for line in f)
    f.close()

    # create OAuth handler and get access
    auth = tweepy.OAuthHandler(c_token, c_secret)
    auth.set_access_token(a_token, a_secret)
                
    # set up listener
    api      = tweepy.API(auth)
    listener = SListener(api)
    
    filterFor = ['nuclear', 'fallout', 'atomic energy', 'nuclear radiation']
    try:    
        stream = tweepy.Stream(auth, listener)    
        stream.filter(track = filterFor)
    except KeyboardInterrupt:
        stream.disconnect()
        'Shutting down, stay safe'
    except:
        print "error"
        stream.disconnect()
    


if __name__ == '__main__':
    main()
