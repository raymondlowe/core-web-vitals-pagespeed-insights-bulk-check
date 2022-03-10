# general setup, common imports
import datetime
from re import L
import secrets as secrets
import shlex
import sys
import time
import os
from urllib.parse import urlparse

import pandas as pd
# import requests
# import requests_cache
from pandas import DataFrame
import tldextract

from cloudflareZones import zones_list

total_counter = 0
so_far_counter = 0

def pagespeed_insight_api(url, strategy, verbose=False, run=1, label=""):
    global so_far_counter

    if verbose:
        print('\nTesting ' + url)
    
    so_far_counter += 1

  # if strategy not in 'mobile' or 'desktop' then default to desktop
    if strategy not in ['mobile', 'desktop']:
        # THROW EXCEPTION
        print('\n' + strategy + ' is not a valid strategy. Defaulting to desktop.')
        strategy = 'desktop'

    if len(label):
        label_str = "&label=" + label
    else:
        label_str = ""

    pagespeed_query_url = 'https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url={}&strategy={}&key={}&run={}{}&utm_source=lighthouse&utm_campaign=core-web-vitals-bulk'.format(
        url, strategy, secrets.api_key, run, label_str)
    # pagespeed_results = urllib.request.urlopen(pagespeed_query_url).read().decode('UTF-8')
    if verbose:
        print(pagespeed_query_url)

    result = session.get(pagespeed_query_url).json()

    # example         "fetchTime": "2022-02-18T08:55:06.255Z",
    try:
        fetch_time = result['lighthouseResult']['fetchTime']
    except:
        #error fetching time
        # print the whole result and exit
        print("error fetching")
        print(result)
        sys.exit()
    # parse fetch_time into datetime using datetime module
    fetch_time = datetime.datetime.strptime(fetch_time, "%Y-%m-%dT%H:%M:%S.%fZ")

      # Performance
    performance = float(result['lighthouseResult']
                        ['categories']['performance']['score'])

    # First Contentful Paint
    first_contentful_paint = float(
        result['lighthouseResult']['audits']['first-contentful-paint']['score'])

    # Speed Index
    speed_index = float(result['lighthouseResult']
                        ['audits']['speed-index']['score'])

    # Largest Contentful Paint
    largest_contentful_paint = float(
        result['lighthouseResult']['audits']['largest-contentful-paint']['numericValue'])  # Largest Contenful Paint

    # audits / largest-contentful-paint-element / details /items /0 / selector
    largest_contentful_paint_element = result['lighthouseResult']['audits']['largest-contentful-paint-element']['details']['items'][0]['node']['selector']

    # Time to Interactive
    time_to_interactive = float(
        result['lighthouseResult']['audits']['interactive']['score'])

    # Total Blocking Time
    total_blocking_time = float(
        result['lighthouseResult']['audits']['total-blocking-time']['numericValue'])

    # Cumulative Layout Shift
    cumulative_layout_shift = float(
        result['lighthouseResult']['audits']['cumulative-layout-shift']['displayValue'])  # CLS

    # # First Input Delay (not one of the main audits)
    # first_input_delay = float(result['loadingExperience']['metrics']['FIRST_INPUT_DELAY_MS']['distributions'][2]['proportion'] )  # First Input Delay as seconds
    combined_result = [url, 
                    fetch_time, 
                    strategy, 
                    run, 
                    performance, 
                    first_contentful_paint,
                    speed_index,
                    largest_contentful_paint,
                    largest_contentful_paint_element,
                    time_to_interactive,
                    total_blocking_time,
                    cumulative_layout_shift,
                    label]
    # if verbose:
    #   print(combined_result)
      
    return combined_result
    # if verbose:
    #   print(pagespeed_results)
    # return json.loads(pagespeed_results)


def pagespeed_list(url_list, platform=False, verbose=False, runs=1, label=""):
    global total_counter 
    global so_far_counter 
    results = []



    for url in url_list:

        # loop runs times
        for run in range(1, runs + 1):

            if platform == 'desktop' or  platform == 'both':
                result_for_url = pagespeed_insight_api(url, 'desktop', verbose, run, label)

                if verbose:
                    print(str(so_far_counter)+"/" +str(total_counter) + ": "+ url + " -> " + str(result_for_url)+ ' complete desktop')
                else:
                    print(str(so_far_counter)+"/" +str(total_counter) + ": "+ url + ' complete desktop')

                results.append(result_for_url)

            if platform == 'mobile' or  platform == 'both':
                result_for_url = pagespeed_insight_api(url, 'mobile', verbose, run, label)

                if verbose:
                    print(str(so_far_counter)+"/" +str(total_counter) + ": "+ url + " -> " + str(result_for_url)+ ' complete mobile')
                else:
                    print(str(so_far_counter)+"/" +str(total_counter) + ": "+ url + ' complete mobile')

                results.append(result_for_url)  

            # print x out of y
            if verbose:
                print("url " + str(url_list.index(url) + 1) + " of " + str(len(url_list)) + " urls, run " + str(run) + " of " + str(runs) + " runs")

    return results

# function find_referenced_urls(url_list)
# takes a list of urls and returns a list of all assets mentioned in the pages as src="..."
# 
def find_referenced_urls(url_list):
    total_counter = len(url_list)
    so_far_counter = 0
    referenced_urls = []

    if verbose:
        print("Scanning {} urls for referenced urls".format(total_counter))

    # make a list of clearable domains from the keys in zones_list
    clearable_domains = []
    for key in zones_list:
        clearable_domains.append(key)

  
  

    for url in url_list:
        so_far_counter += 1
        if verbose:
            print(str(so_far_counter)+"/" +str(total_counter) + ": "+ url + ' fetching')

        # get the html
        html = requests.get(url).text

        # find all the src="..." and href="..."
        src_urls = re.findall('src="(.*?)"', html) + re.findall('<link.*href=["|\'](.*?)["|\']', html)
        
        # if the url is relative then use the current url root to make it absolute
        for src_url in src_urls:
            if src_url.startswith("//"):
                src_url = "https:" + src_url
            if src_url.startswith("/"):
                src_url = urlparse(url).scheme + "://" + urlparse(url).netloc + src_url
            # if the src_url is for the same domain as url then add it to the list
            if urlparse(src_url).netloc == urlparse(url).netloc:
                if src_url not in referenced_urls:
                    # get the hostname without www subdomain

                    hostname = tldextract.extract(src_url).registered_domain
                    
                    if hostname in clearable_domains:
                        referenced_urls.append(src_url)

                    

    return referenced_urls

# set up requests_cache
# requests_cache.install_cache('pagespeed_cache')
from requests_cache import CachedSession
session = CachedSession('pagespeed_cache')
import requests
import re
uncached_session = requests.Session()

# main so this can be imported as a module
if __name__ == '__main__':

    total_counter = 0
    so_far_counter = 0


    # use argparse to get command line arguments
    import argparse
    # import argparse file format type
    from argparse import FileType

    parser = argparse.ArgumentParser(
        description='Get PageSpeed Insights results for a list of URLs')
    # main argument is filename of urls list
    parser.add_argument(
        'url_list_file', help='file containing list of URLs to test', type=FileType('r'))
    # argument --platform can be 'desktop' 'mobile' or 'both'.  the default is 'both'
    parser.add_argument('--platform', choices=['desktop', 'mobile', 'both'],
                        help='platform to test [desktop|mobile|both], default both ', default='both')
    parser.add_argument('--verbose', action='store_true', default=False,
                        help='Print more details to stdout, default False')
    parser.add_argument('--nocache', action='store_true', default=False,
                        help='Without caching and clearing cache, default False')
    parser.add_argument('--clearcloudflare', action='store_true', default=False,
                        help='Clear the CloudFlare cache of all pages before testing, default False')                       
    parser.add_argument('--runs', type=int, default=1,
                        help='Number of times to run PageSpeed Insights default 1')
    parser.add_argument('--csv', type=str, nargs="?", const="pagespeed-insights-bulk.csv",
                        help='Optional: csv to *append* results to: default pagespeed-insights-bulk.csv')
    parser.add_argument('--xlsx', type=str, nargs="?", const='core-web-vitals-bulk-' + \
                                                                time.strftime('%Y%m%d-%H%M%S') + '.xlsx',
                        help='Optional: xlsx to be created with results to: default core-web-vitals-bulk-<datetime>_<label>.xlsx')
    parser.add_argument('--label', type=str, default="",
                        help='Optional label; effects caching and output filename default none/blank')
    args = parser.parse_args()

    # get the input filename from the first arg that isn't a switch
    input_file = args.url_list_file

    platform = args.platform
    verbose = args.verbose
    runs = args.runs
    nocache = args.nocache
    clearcloudflare = args.clearcloudflare
    label = args.label
    csvfilename = args.csv
    xl_filename = args.xlsx

    if (csvfilename is None) and (xl_filename is None):
        print("No output file specified, exiting")
        exit(1)

    if verbose:
        print('\nRunning PageSpeed Insights ' + str(runs) +
              ' time(s) for ' + platform + ' platform(s) in verbose mode')
        print('\nCache db is ' + str(session.cache.db_path))

        # print csv filename if it exists
        if csvfilename is not None:
            print('\nCSV output file: ' + csvfilename)
        
        # print xlsx filename if it exists
        if xl_filename is not None:
            if len(label) > 0:
                # insert the label into the xl_filename
                xl_filename = xl_filename.replace('.xlsx', '_' + label + '.xlsx')

            print('\nXLSX output file: ' + xl_filename)


    if nocache:
        # set session expire to 0
        session.expire_after = 0
        if verbose:
            print('\nExpiring cached results and loading fresh data from server')


    # read the input_filename text file into a list called url_list
    url_list = []
    with input_file as f:
        for line in f:
            url_list.append(line.strip())

    if verbose:
        print('\nurl_list is {} urls'.format(len(url_list)))
        print('\n')


    if clearcloudflare:
        if verbose:
            print('\nClearing CloudFlare cache of all pages before testing')

        clearcloudflare_url_list = url_list + find_referenced_urls(url_list)

        if verbose:
            print('\nClear CloudFlare list is {} urls'.format(len(clearcloudflare_url_list)))
            print('\n')

        # use api to clear the cloudflare cache of all pages in the clearcloudflare_url_list
        for url in clearcloudflare_url_list:
            if verbose:
                print('\nClearing CloudFlare cache of ' + url)
            
            # check which domain this url is and get the api email and key from the zones_list
            domain = tldextract.extract(url).registered_domain
            if domain in zones_list:
                email = zones_list[domain]['email']
                key = zones_list[domain]['key']

                # get the cloudflare api url
                cloudflare_api_url = 'https://api.cloudflare.com/client/v4/zones/' + \
                    zones_list[domain]['zoneid'] + '/purge_cache'
                
                # set the headers for the email and the api_key
                headers = {'X-Auth-Email': email, 'X-Auth-Key': key}

                # set the data for the request to purge just this url
                data = {'files': [url]}

                # make the request
                r = uncached_session.post(cloudflare_api_url, headers=headers, json=data)

                if r.status_code != 200:
                    print('\nCloudFlare purge request failed for ' + url)
                    print('\nError: ' + r.text)
                    print('\n')
                else:
                    if verbose:
                        print('\nCloudFlare purge request successful for ' + url)
                        print('\n')


 
    total_counter = len(url_list) * runs
    if platform == 'both':
        total_counter = total_counter * 2

    # run the pagespeed_list function on the url_list

    results = pagespeed_list(url_list, platform=platform, verbose=verbose, runs=runs, label=label)


    # Convert to dataframe and export as excel
    results_df = DataFrame(results, columns=['URL',
                                                'fetch date',
                                                'platform',
                                                'run number',
                                                'performance',
                                                'first contentful paint',
                                                'speed index',
                                                'largest contentful paint',
                                                'largest contentful paint element',
                                                'time to interactive',
                                                'total blocking time',
                                                'cumulative layout shift',
                                                'label'])  

    if xl_filename is not None:

        optionsdf = pd.DataFrame(
            {'options': [" ".join(map(shlex.quote, sys.argv[1:]))]})
        excelwriter = pd.ExcelWriter(xl_filename)
        results_df.to_excel(excelwriter, sheet_name='Data')
        optionsdf.to_excel(excelwriter, sheet_name='Options')
        excelwriter.save()
        print('\nResults saved to ' + xl_filename)

    if csvfilename is not None:
        # if text file called csvfilename doesn't exist then create it with headers
        if not os.path.isfile(csvfilename):
            with open(csvfilename, 'w') as f:
                f.write('Index,URL,fetch date,platform,run number,performance,first contentful paint,speed index,largest contentful paint,largest contentful paint element,time to interactive,total blocking time,cumulative layout shift,label\n')
            if verbose:
                print('\nCreated csv file ' + csvfilename)
        
        
        # append results_df to csvfile
        results_df.to_csv(csvfilename, mode='a', header=False)
        print('\nResults appended to ' + csvfilename)


    print('\nDone!')
