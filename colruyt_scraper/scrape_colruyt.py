# import external modules
import os
import sys
import json
import time
import pandas
import random
import requests
import argparse
import concurrent.futures
from functools import partial

# import local modules
from urls_public import COLRUYT_PRODUCTS_API_BASEURL
from urls_public import COLRUYT_PRODUCTS_API_ENDPOINT
from urls_private import XCG_API_KEY
from urls_private import USER_AGENT


def get_products(searchterm, page=1, products_per_page=1, shopid=604, useproxy=False):
    '''
    Get list of products matching search criteria
    
    Input arguments:
    - searchterm: string representing search term (required in Colruyt API)
    - page: number of page to return
    - products_per_page: number of results to return per page
    - shopid: identification code of shop
    - useproxy: whether to make an API call via a proxy server
    '''
    # make valid API URL
    apiurl = COLRUYT_PRODUCTS_API_BASEURL + COLRUYT_PRODUCTS_API_ENDPOINT
    # define parameters to pass to the search query of the request
    params = {
        "clientCode": "clp",
        "page": int(page),
        "placeId": int(shopid),
        "size": int(products_per_page),
        "sort": "popularity asc",
        "searchTerm": str(searchterm)
    }
    # define headers
    headers = {
        "user-agent": USER_AGENT,
        "x-cg-apikey": XCG_API_KEY
    }
    if useproxy: return make_api_call_proxy(apiurl, params=params, headers=headers)
    else: return make_api_call(apiurl, params=params, headers=headers)


def make_api_call(url, params=None, headers=None):
    '''Make call to Colruyt API with given parameters'''
    try:
        response = requests.get(url, params=params, headers=headers)
    except (requests.exceptions.ProxyError,
            requests.exceptions.ConnectTimeout,
            requests.exceptions.SSLError) as e:
        msg = "ERROR in make_api_call: {}".format(e)
        print(msg)
    except Exception as e:
        msg = "ERROR in make_api_call: {}".format(e)
        print(msg)
        return None
    status = response.status_code
    if status != 200:
        text = response.text
        text_threshold = 400
        msg = "ERROR in make_api_call: response has status code {}".format(status)
        if len(text) < text_threshold: msg += " ({})".format(text)
        else:
            msg += '({} [message terminated'.format(text[:text_threshold])
            msg += ' after {} characters])'.format(text_threshold)
        print(msg)
    try:
        responsejson = response.json()
    except Exception as e:
        msg = "ERROR in make_api_call_proxy: response could not be converted to json."
        print(msg)
        return None
    return responsejson


def make_api_call_proxy(url, params=None, headers=None):
    '''Make call to Colruyt API with given parameters, using a proxy server'''
    # import local module for handling proxy requests
    from proxy_requests import ProxyRequests
    try:
        request = ProxyRequests(url)
        request.get(params=params, headers=headers)
    except (requests.exceptions.ProxyError,
            requests.exceptions.ConnectTimeout,
            requests.exceptions.SSLError) as e:
        msg = "ERROR in make_api_call_proxy: {}".format(e)
        print(msg)
    except Exception as e:
        msg = "ERROR in make_api_call_proxy: {}".format(e)
        print(msg)
        return None
    status = request.rdata['status_code']
    if status != 200:
        text = request.rdata['request']
        text_threshold = 400
        msg = "ERROR in make_api_call_proxy: response has status code {}".format(status)
        if len(text) < text_threshold: msg += " ({})".format(text)
        else:
            msg += '({} [message terminated'.format(text[:text_threshold])
            msg += ' after {} characters])'.format(text_threshold)
        print(msg)
    try:
        responsejson = request.rdata['json']
    except Exception as e:
        msg = "ERROR in make_api_call_proxy: response could not be converted to json."
        print(msg)
        return None
    return responsejson


def process_products(response_json):
    '''Extract useful info from products response object'''
    if response_json is None:
        msg = "ERROR: response_json is None"
        print(msg)
        return None
    if response_json.get("products") is None:
        msg = "ERROR: products attribute of response_json is None"
        print(msg)
        return None
    products_json = response_json.get("products")
    products = []
    for product_json in products_json: products.append( process_product(product_json) )
    return products


def process_product(product_json):
    '''Process a single product'''
    product_dict = {}
    product_dict['name'] = product_json.get('LongName')
    product_dict['content'] = product_json.get('content')
    product_dict['unitprice'] = product_json.get('price').get('measurementUnitPrice')
    product_dict['priceunit'] = product_json.get('price').get('measurementUnit')
    return product_dict


def scrape(searchterm, page, products_per_page=1, shopid=604, useproxy=False):
    print("Process page " + str(page))
    response_json = get_products(searchterm,
            page=page, products_per_page=products_per_page,
            shopid=shopid, useproxy=useproxy)
    if( response_json is None ):
        msg = "ERROR in scrape: returned json object is None"
        print(msg)
        return None
    if( response_json.get("productsReturned") is None ):
        msg = "ERROR in scrape: productsReturned attribute is None"
        print(msg)
        return None
    if( response_json.get("productsReturned") == 0 ):
        msg = "WARNING in scrape: productsReturned attribute is 0"
        print(msg)
        return None
    products = process_products(response_json)
    print(">>> process page " + str(page) + " done.")
    return products


########
# main #
########

if __name__=='__main__':

    # read command line args
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--searchterm', required=True)
    parser.add_argument('-p', '--npages', type=int, default=1)
    parser.add_argument('-t', '--nthreads', type=int, default=1)
    parser.add_argument('-o', '--outputfile', default=None)
    parser.add_argument('--products_per_page', type=int, default=25)
    parser.add_argument('--shopid', type=int, default=604)
    parser.add_argument('--useproxy', default=False, action='store_true')
    args = parser.parse_args()

    # argument parsing
    pages = range(1, args.npages+1)
    kwargs = {
      'products_per_page': args.products_per_page,
      'shopid': args.shopid,
      'useproxy': args.useproxy
    }

    # run test without concurrency
    #print('Running local test...')
    #products = scrape(args.searchterm, pages[0], **kwargs)
    #print('Local test done, found {} products.'.format(len(products)))

    # run scraping
    searchterm_repeat = [args.searchterm]*len(pages)
    partial_scrape = partial(scrape, **kwargs)
    print('Running production...')
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.nthreads) as executor:
        products = executor.map(partial_scrape, searchterm_repeat, pages)
    products = [product for product in products if product is not None]
    print('Production done, found {} products.'.format(len(products)))
    if len(products)==0: sys.exit()

    # convert to dataframe and save to file
    df = pandas.DataFrame(products)
    print(df)
    if args.outputfile is not None: df.to_csv(args.outputfile)
