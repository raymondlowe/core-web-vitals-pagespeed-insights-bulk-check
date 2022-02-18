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

    largest_contentful_paint = result['lighthouseResult']['audits']['largest-contentful-paint']['displayValue'].replace(u'\xa0', u'') # Largest Contenful Paint
    first_input_delay = str(round(result['loadingExperience']['metrics']['FIRST_INPUT_DELAY_MS']['distributions'][2]['proportion'] * 1000, 1)) + 'ms' # First Input Delay
    cumulative_layout_shift = result['lighthouseResult']['audits']['cumulative-layout-shift']['displayValue'] # CLS

    # trim trailing s from largest_contentful_paint
    if largest_contentful_paint[-1] == 's':
      largest_contentful_paint = largest_contentful_paint[:-1]
    
    # trim trailing ms from first_input_delay
    if first_input_delay[-2:] == 'ms':
      first_input_delay = first_input_delay[:-2]


    result_url = [url,float(largest_contentful_paint),float(first_input_delay),float(cumulative_layout_shift)]
    if verbose:
      print(result_url)


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
    print('-v or --verbose: print out the json results')
    print('-d or --desktop: run the pagespeed analysis on a desktop browser')
    print('-c or --clear-cache: clear the requests-cache cache')

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
  results_df = DataFrame (results,columns=['URL','LCP (s)','FID (ms)','CLS'])
  # output to excel file with datetime in the filename
  output_filename = 'core-web-vitals-bulk-' + time.strftime('%Y%m%d-%H%M%S') + '.xlsx'

  optionsdf = pd.DataFrame({'options': [" ".join(map(shlex.quote, sys.argv[1:]))]})
  excelwriter=pd.ExcelWriter(output_filename)
  results_df.to_excel(excelwriter, sheet_name='Data')
  optionsdf.to_excel(excelwriter, sheet_name='Options')
  excelwriter.save()
  print('\nResults saved to ' + output_filename)
  print('\nDone!')


