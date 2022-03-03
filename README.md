# core-web-vitals-pagespeed-insights-bulk
Use google API of pagespeed insights to get the core web vitals of a list of urls

## Based on

Based on :

https://colab.research.google.com/drive/1dvldrLnrpNPu0lAu9sZRV_jJMJiET56b?usp=sharing

## Usage
```
usage: core-web-vitals-bulk.py [-h] [--platform {desktop,mobile,both}] [--verbose] [--nocache] [--runs RUNS]
                               [--label LABEL] [--csv [CSV]] [--xlsx [XLSX]]
                               url_list_file

Get PageSpeed Insights results for a list of URLs

positional arguments:
  url_list_file         file containing list of URLs to test

options:
  -h, --help            show this help message and exit
  --platform {desktop,mobile,both}
                        platform to test [desktop|mobile|both], default both
  --verbose             Print more details to stdout, default False
  --nocache             Without caching and clearing cache, default False
  --runs RUNS           Number of times to run PageSpeed Insights default 1
  --csv [CSV]           Optional: csv to *append* results to: default pagespeed-insights-bulk.csv
  --xlsx [XLSX]         Optional: xlsx to be created with results to: default core-web-vitals-
                        bulk-<datetime>_<label>.xlsx
  --label LABEL         Optional label; effects caching and output filename default none/blank

```

At least one of `--csv` or `--xlsx` must be specified, filenames are optional. To avoid confusion 
don't use these options without a filename immediately before specifying the url_list_file.

## Installation / setup

Clone this repo.

```
git clone https://github.com/raymondlowe/core-web-vitals-pagespeed-insights-bulk-check.git
```


Install requirements
```
cd core-web-vitals-pagespeed-insights-bulk-check
pip install -r requirements.txt
```

Create your own Google API key from the cloud console, optionally restrict it to just pagespeed api.

Go to:

https://console.cloud.google.com/apis/credentials


Click: 
* CREATE CREDENTIALS

Wait for the key to be made, can be used immediately, or use RESTRICT KEY to restrict it.

Optionally name the key so it isn't "API key <n>"

Put the API key in a file named `secrets.py` located in the same folder.

```
api_key ="<your key here>"
```

Do a manual run so you can ensure the api is activated:

https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url=https://example.com/&key={your_key}


