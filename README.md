# readme-fads
===========

what can we learn from the README files from the best Github repos?

## Demo
http://107.170.114.168/index.html
A live demo of the results of this project

## Requirements
- Python 3
- pip for installing pyquery, pygithub
- access to the github API (no need to auth)
- site is in pure HTML (for the time being)

## How to
- readme-scrapper-condenser.py gets the top 150 most starred README files (as rendered HTML) of the most popular languages of Github
- readme-scrapper-condenser.py also does the data wrangling by accessing each README file with pyquery to get the interesting parts
- site displays the output (python script outputs json files) in a somewhat attractive way

### ye be warned: github's api has quite strict limits so workaround this fact or use the readme files in this repo (folder readme_files)

