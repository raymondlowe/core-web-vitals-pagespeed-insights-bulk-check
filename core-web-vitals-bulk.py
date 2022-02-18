# general setup, common imports
import json, requests, time, urllib.parse
import pandas as pd
from pandas import DataFrame
import sys
import io
import secrets as secrets
import shlex



def pagespeed_insight_api(url, desktop=False, verbose = False):
  if verbose:
    print('\nTesting ' + url)
  if desktop:
    strategy = 'desktop'
  else:
    strategy = 'mobile'
  pagespeed_query_url = 'https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url={}&strategy{}&key={}'.format(url,strategy,secrets.api_key)
  # pagespeed_results = urllib.request.urlopen(pagespeed_query_url).read().decode('UTF-8')
  return requests.get(pagespeed_query_url).json()
  # if verbose:
  #   print(pagespeed_results)
  # return json.loads(pagespeed_results)


def pagespeed_list(url_list, desktop=False, verbose = False):
  results = []

  for url in url_list:
    

    result = pagespeed_insight_api(url, desktop, verbose)

    # Performance
    performance = float(result['lighthouseResult']['categories']['performance']['score'])


    # First Contentful Paint
    first_contentful_paint = float(result['lighthouseResult']['audits']['first-contentful-paint']['score'])


    # Speed Index
    speed_index = float(result['lighthouseResult']['audits']['speed-index']['score'])

    # Largest Contentful Paint
    largest_contentful_paint = float(result['lighthouseResult']['audits']['largest-contentful-paint']['numericValue']) # Largest Contenful Paint


    # Time to Interactive
    time_to_interactive = float(result['lighthouseResult']['audits']['interactive']['score'])

    # Total Blocking Time
    total_blocking_time = float(result['lighthouseResult']['audits']['total-blocking-time']['numericValue'])

    # Cumulative Layout Shift
    cumulative_layout_shift = float(result['lighthouseResult']['audits']['cumulative-layout-shift']['displayValue']) # CLS


    # # First Input Delay (not one of the main audits)
    # first_input_delay = float(result['loadingExperience']['metrics']['FIRST_INPUT_DELAY_MS']['distributions'][2]['proportion'] )  # First Input Delay as seconds



    result_url = [url, performance, first_contentful_paint ,\
                  speed_index ,\
                  largest_contentful_paint ,\
                  time_to_interactive ,\
                  total_blocking_time ,\
                  cumulative_layout_shift  ]
    if verbose:
      print(url + " -> " + str(result_url))
    else:
      print(url + ' complete')

    results.append(result_url)

  return results

#set up requests_cache
import requests_cache
requests_cache.install_cache('pagespeed_cache')


# main so this can be imported as a module
if __name__ == '__main__':
  # get the input filename from the first arg that isn't a switch
  input_filename = None
  for i in range(1, len(sys.argv)):
    if sys.argv[i][0] != '-':
      input_filename = sys.argv[i]
      break
  

  # if -v or --verbose is on the arguments then set verbose to True
  verbose = False
  if '-v' in sys.argv or '--verbose' in sys.argv:
    verbose = True
    print('Verbose mode on')
    print('input filename is ' + input_filename)

# if -c or --clear-cache is one of the arguments then clear the requests-cache cache
  if '-c' in sys.argv or '--clear-cache' in sys.argv:
    requests_cache.clear()
    if verbose:
      print('Cache cleared')

  # if -d or --desktop then set desktop to True
  desktop = False
  if '-d' in sys.argv or '--desktop' in sys.argv:
    desktop = True
    if verbose:
      print('Desktop mode')

  # if -h or --help is on the arguments then print help and exit
  if ('-h' in sys.argv or '--help' in sys.argv) or (input_filename is None):
    print('Usage: python3 core-web-vitals-bulk.py [text file with list of urls]')
    print('-v or --verbose: print more verbose details to the screen, no change to final report')
    print('-d or --desktop: run the pagespeed analysis on a desktop browser otherwise it uses mobile mode for the test')
    print('-c or --clear-cache: clear the requests-cache cache otherwise old cached data will be used')

    sys.exit(0)


  # read the input_filename text file into a list called url_list
  url_list = []
  with open(input_filename, 'r') as f:
    for line in f:
      url_list.append(line.strip())

  if verbose:
    print('\n\n\n')
    print('url_list is {} urls'.format(len(url_list)))

  # run the pagespeed_list function on the url_list
  
  results = pagespeed_list(url_list, desktop, verbose)

  #Convert to dataframe and export as excel
  results_df = DataFrame (results,columns=['URL',
                                            'performance',\
                                            'first contentful paint',\
                                            'speed index',\
                                            'largest contentful paint',\
                                            'time to interactive',\
                                            'total blocking time',\
                                            'cumulative layout shift']) #,\
                                            # 'first input delay'])



  # output to excel file with datetime in the filename
  output_filename = 'core-web-vitals-bulk-' + time.strftime('%Y%m%d-%H%M%S') + '.xlsx'

  optionsdf = pd.DataFrame({'options': [" ".join(map(shlex.quote, sys.argv[1:]))]})
  excelwriter=pd.ExcelWriter(output_filename)
  results_df.to_excel(excelwriter, sheet_name='Data')
  optionsdf.to_excel(excelwriter, sheet_name='Options')
  excelwriter.save()
  print('\nResults saved to ' + output_filename)
  print('\nDone!')


