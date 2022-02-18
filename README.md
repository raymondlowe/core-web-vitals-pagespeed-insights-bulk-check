# core-web-vitals-pagespeed-insights-bulk
Use google API of pagespeed insights to get the core web vitals of a list of urls

## Based on

Based on :

https://colab.research.google.com/drive/1dvldrLnrpNPu0lAu9sZRV_jJMJiET56b?usp=sharing

## Usage
```
Usage: python3 core-web-vitals-bulk.py [text file with list of urls]
-v or --verbose: print out the json results
-d or --desktop: run the pagespeed analysis on a desktop browser
-c or --clear-cache: clear the requests-cache cache
```
## Installation / setup

Clone this repo.

Create your own Google API key from the cloud console, optionally restrict it to just pagespeed api, and the put it in a file in the same folder as `secrets.py`

```
api_key ="<your key here>"
```
