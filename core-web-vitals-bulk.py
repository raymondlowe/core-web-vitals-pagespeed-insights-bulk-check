# general setup, common imports
import datetime
from re import L
import secrets as secrets
import shlex
import sys
import time
import os

import pandas as pd
# import requests
# import requests_cache
from pandas import DataFrame


def pagespeed_insight_api(url, strategy, verbose=False, run=1, label=""):
    if verbose:
        print('\nTesting ' + url)

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
    fetch_time = result['lighthouseResult']['fetchTime']
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
    results = []

    for url in url_list:

        # loop runs times
        for run in range(1, runs + 1):


          if platform == 'desktop' or  platform == 'both':
            result_for_url = pagespeed_insight_api(url, 'desktop', verbose, run, label)

            if verbose:
                print(url + " -> " + str(result_for_url))
            else:
                print(url + ' complete')

            results.append(result_for_url)

          if platform == 'mobile' or  platform == 'both':
            result_for_url = pagespeed_insight_api(url, 'mobile', verbose, run, label)

            if verbose:
                print(url + " -> " + str(result_for_url))
            else:
                print(url + ' complete')

            results.append(result_for_url)

    return results


# set up requests_cache
# requests_cache.install_cache('pagespeed_cache')
from requests_cache import CachedSession
session = CachedSession('pagespeed_cache')

# main so this can be imported as a module
if __name__ == '__main__':

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
    parser.add_argument('--runs', type=int, default=1,
                        help='Number of times to run PageSpeed Insights default 1')
    parser.add_argument('--label', type=str, default="",
                        help='Optional label; effects caching and output filename default none/blank')
    parser.add_argument('--csvfile', type=str, nargs="?", const="pagespeed-insights-bulk.csv",
                        help='Optional: csv to *append* results to: default pagespeed-insights-bulk.csv')
    args = parser.parse_args()

    # get the input filename from the first arg that isn't a switch
    input_file = args.url_list_file

    platform = args.platform
    verbose = args.verbose
    runs = args.runs
    nocache = args.nocache
    label = args.label
    csvfilename = args.csvfile


    if verbose:
        print('\nRunning PageSpeed Insights ' + str(runs) +
              ' time(s) for ' + platform + ' platform(s) in verbose mode')
        print('\nCache db is ' + str(session.cache.db_path))


    if nocache:
        # set session expire to 0
        session.expire_after = 0
        if verbose:
            print('\nNot using cache')


    # read the input_filename text file into a list called url_list
    url_list = []
    with input_file as f:
        for line in f:
            url_list.append(line.strip())

    if verbose:
        print('\n\n\n')
        print('url_list is {} urls'.format(len(url_list)))
        print('\n\n\n')
        if csvfilename is not None:
            print('csvfilename: {}'.format(csvfilename))
        else:
            print('csvfilename: None')


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


    if len(label) > 0:
        label = '_' + label
    # output to excel file with datetime in the filename
    output_filename = 'core-web-vitals-bulk-' + \
        time.strftime('%Y%m%d-%H%M%S') + label + '.xlsx'

    optionsdf = pd.DataFrame(
        {'options': [" ".join(map(shlex.quote, sys.argv[1:]))]})
    excelwriter = pd.ExcelWriter(output_filename)
    results_df.to_excel(excelwriter, sheet_name='Data')
    optionsdf.to_excel(excelwriter, sheet_name='Options')
    excelwriter.save()
    print('\nResults saved to ' + output_filename)

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
