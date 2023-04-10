# toll_booth_finder

This is a small project that I am working on for a friend. I'm extremely busy with university and side-projects right now so code is poorly written and sparsely commented. This is a minimum-working version of the code.

This code returns up to four toll booths that may be crossed on a certain specified route. This script was made for assisting in statistical analysis. I doubt this will be useful to anyone other than my friend, but if someone wants to adapt the code for their own uses, go ahead (please read licence). If you have any questions you can reach me at teddixon@umich.edu.

# Setup

1. get a google places API key and put it in the .env file as: GOOGLE_MAPS_API_KEY=YOUR_KEY_HERE
2. run setup.py to install dependencies
3. add your "input.xlsx" to the working directory
4. add your blank "output.tsv" to the working directory


The format of "input.xlsx" should be as follows:
- row 1 is headers and is thrown out
- col 1 must be ID
- col 3 must be the starting city
- col 4 must be the destination city
- cols 5-8 must either be a waypoint city or blank
