tweiger_counter
===============

python &amp; arduino code for a arduino geiger counter that streams tweets, 
screens for keywords around nuclear and maps the tweets per minute - warning
you of the next Fukushima or nuclear war (or maybe breakthrough in nuclear physics)

code for the following instructable
http://www.instructables.com/id/the-tweiger-counter/

if you want to search for other keywords, you can either change the code or just start
the script from the command line with the words as commandline arguments:

  >>> user@computer c/tweiger_counter/ $ python tweiger_counter.py keyword1 keyword2 ... maximum
  
you can pass as many keywords as you want. the normalization argument lets you define
for which number of tweets per minute the maximum will be reached. by that you can scale your counter.
starting from IDLE or without arguments will just call standard keywords

the script should automatically detect which operating system you run and try to connect to the arduino 
on the standard port ("COM4" for windows and "/dev/ttyACM0" for linux). if you can't connect, make sure 
you are using the right port.
