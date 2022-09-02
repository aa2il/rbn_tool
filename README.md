# RBN Analysis Tool

Tool to analyze the spot data from the Reverse Beacon Network.  I originally developed this because I was interested in where I was being heard.  Like all the other apps in this repository, this is a work in progress.

Example usage - To see where I was being heard while running during one of the recent CWTs (0300 session on July 28, 2022), first download the data for that day from https://www.reversebeacon.net/raw_data/ and then run
                                                
rbn_tool.py 20220728.csv -t1 3 -hours 1 -na

-t1 specifies the start time in hours UTC
-hours specifies the duration of the interval of interest
-na filters spots to only those in North America 

![Screen Shot]( Docs/rbn.png)

The white blobs are all the skimmers that reported spots during that interval.
The Orange blob is my QTH in DM12.
The red x's indicate the skimmers that spotted me on 20m.
The blue +'s indicate the skimmers that spotted me on 40m.

Inspired by some results presented recently by N3QE on the CWops email reflector, I've added a second plot showing the speed distribution of the spots in this time interval:

![Screen Shot]( Docs/speed.png)

Contests spanning multiple days are handled by specifying multiple spot files.  To see the speed distribution from last year's NAQP CW contest:

rbn_tool.py 2021080[78].zip -t1 18 -hours 12 -na

![Screen Shot]( Docs/naqpcw_aug2021.png)

Here is the speed distribution for the recent IARU HF Championships:

rbn_tool.py 20220709.zip 20220710.zip -t1 12 -hours 24 -na

![Screen Shot]( Docs/iaru_2022.png)

