# RBN Analysis Tool

Tool to analyze spot date from the Reverse Beacon Network.

Example usage - To see where I was being heard while running during one of the recent CWTs (0300 session on July 28, 2022), first download and unpack the data for that day from https://www.reversebeacon.net/raw_data/ and then run
                                                
rbn_tool.py 20220728.csv -t1 3 -hours 1 -na

![Screen Shot]( Docs/rbn.png)

Inspired by some results presented recently by N3QE on the CWops email reflector, I've added a second plot showing the speed distribution of the spots in this time interval:

![Screen Shot]( Docs/speed.png)

Contests spanning multiple days are handled by specifying multiple spot files.  To see the speed distribution from last year's NAQP CW contest:

rbn_tool.py 2021080[78].csv -t1 18 -hours 12 -na

![Screen Shot]( Docs/naqpcw_aug2021.png)

Update: Can now read RBN zip files directly without unpacking.  Here is the speed distribution for the recent IARU HF Championships:

rbn_tool.py 20220709.zip 20220710.zip -t1 12 -hours 24 -na

![Screen Shot]( Docs/iaru_2022.png)

