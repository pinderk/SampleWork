from lxml import html
import requests
import bs4
from bs4 import BeautifulSoup
import math
import time

#last edited by Kyle at 6:53pm, March 8

def parse_url(url):
    '''
    Requests the html of the given url and returns a dictionary of the urls 
    of each home that came up in the page of results to their 
    latitude/longitude location.

    Inputs:
        url: (string) The url of the page of search results.

    Outputs:
        url_loc: (dict) The dictionary mapping the house urls to their 
                 latitude/longitude location.
        soup: The html content of the url page.
    '''

    url_list = []
    lat_list = []
    lon_list = []
    lat_lon_list = []
    url_loc = {}

    #https://www.scrapehero.com/how-to-prevent-getting-blacklisted-while-scraping/
    request_headers = {'accept': 'text/html,application/xhtml+xml,application\
                        /xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                       'accept-encoding': 'gzip, deflate, br',
                       'accept-language': 'en-US,en;q=0.8',
                       'upgrade-insecure-requests': '1',
                       'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; \
                        x64) AppleWebKit/537.36 (KHTML, like Gecko) \
                        Chrome/61.0.3163.100 Safari/537.36'}

    request_headers_1 = {'accept':'text/html,application/xhtml+xml,\
                          application/xml;q=0.9,image/webp,*/*;q=0.8',
                         'accept-encoding':'gzip, deflate, sdch, br',
                         'accept-language':'en-GB,en;q=0.8,en-US;q=0.6,ml;\
                          q=0.4',
                         'cache-control':'max-age=0',
                         'upgrade-insecure-requests':'1',
                         'user-agent':'Mozilla/5.0 (X11; Linux x86_64) \
                          AppleWebKit/537.36 (KHTML, like Gecko) \
                          Chrome/56.0.2924.87 Safari/537.36'}

    with requests.Session() as a:
        response = a.get(url, headers=request_headers)

    soup = BeautifulSoup(response.content, "lxml") 
    url_list = []

    href = [n["href"] for n in soup.find_all("a", href = True)]
    hd_list = [i for i in href if "homedetails" in i]

    if len(hd_list) == 0:
        print("switching headers")
        with requests.Session() as a:
            response = a.get(url, headers=request_headers_1)
        soup = BeautifulSoup(response.content, "lxml")

    href = [n["href"] for n in soup.find_all("a", href = True)]
    hd_list = [i for i in href if "homedetails" in i]

    for hd in hd_list:
        url_list.append("http://www.zillow.com/homes/for_sale" + hd)

    lat = [m["data-latitude"] for m in soup.find_all("article")]
    for l in lat:
        lat_list.append(l[:2] + "." + l[2:])
    
    lon = [m["data-longitude"] for m in soup.find_all("article")]
    for l in lon:
        lon_list.append(l[:3] + "." + l[3:])

    for r in range(len(lat_list)):
        lat_lon_list.append([lat_list[r], lon_list[r]])

    print(len(url_list), len(lat_lon_list))
    if len(url_list) == len(lat_lon_list):
        for r in range(len(url_list)):
            url_loc[url_list[r]] = lat_lon_list[r]
    else:
        print("some data is missing for some of the homes that appeared in the search")
        url_loc[1] = 2 

    return url_loc, soup


def find_num_pages(soup, initial_url, misc):
    '''
    Finds the total number of homes returned by the search results, 
    and calculates the total number of pages to crawl for data.

    Inputs:
        soup: The html content of the page.
        initial_url: (string) The url of the initial page of results.
        misc: (string) The type of results that will be returned 
              (either all results put up in the last day or available 
              results given other parameters).

    Outputs:
        page_counter: (int) The total number of pages to crawl.
        tot_num: (int) The total number of results returned by 
                 the search criteria.
    '''

    if misc != "ONLY NEW":
        n = str(soup.find_all("title"))
    
        if len(n) == 2:
            print("couldn't get title, trying again")
            while True:
                time.sleep(2)
                url_loc, soup = parse_url(initial_url)
                n = str(soup.find_all("title"))
                print(n)
                if len(n) > 2:
                    break
                else:
                    print("trying again")
                    continue 
        
        raw_num = n[-31:-24].strip()
        if "-" in raw_num:
            raw_num = raw_num[raw_num.index("-")+1:]
        if "," in raw_num:
            raw_num = raw_num[0:raw_num.index(",")]+raw_num\
                      [raw_num.index(",")+1:]
        if "e -" in raw_num:
            raw_num = raw_num[-1]
        raw_num = raw_num.split()[0]
        tot_num = int(raw_num)
        print(tot_num)

    elif misc == "ONLY NEW":
        n = soup.find_all("meta")

        if len(n) == 0:
            print("couldn't get title, trying again")
            while True:
                time.sleep(2)
                url_loc, soup = parse_url(initial_url)
                n = [m["content"] for m in soup.find_all("meta")]
                if len(n) > 0:
                    break
                else:
                    print("trying again")
                    continue

        raw_string = str(n[2])
        rsl = raw_string[26:31].split()
        raw_num = rsl[0]
        tot_num = int(raw_num)    
        print(tot_num)   

    if tot_num == 0:
        print("There were no results that matched the search criteria")

    page_counter = math.ceil(int(tot_num)/25)

    return page_counter, tot_num


def get_all_results(min_beds, min_baths, min_price, max_price, 
                    neighborhood, misc):
    '''
    Returns a dictionary mapping the urls of each house the fits the search 
    criteria to their latitude/longitude location and its price,
    number of beds, and number of baths.

    Inputs:
        min_beds: (int) The minimum number of beds desired by the user.
        min_baths: (int or float) The minimum number of baths desired 
                   by the user.
        min_price: (int) The minimum price of the house desired by the user.
        max_price: (int) The maximum price of the house desired by the user.
        neighborhood: (string) The neighborhood from which the user wants 
                      search results returned.
        misc: (string) The type of results that will be returned 
              (either all results put up in the last day or available results 
              given other parameters).

    Outputs:
        (url_loc, neighborhood): A tuple containing the dictionary mapping 
                                 house urls to their respective information 
                                 and the neighborhood.
    '''

    if min_price == 0:
        min_price = 1

    if misc == "sale":
        initial_url = "https://www.zillow.com/homes/for_sale/" + neighborhood\
                       + "-Chicago-IL/" + str(min_beds) + "-_beds/" + \
                       str(min_baths) + "-_baths/" + str(min_price) + "-" + \
                       str(max_price) + "_price/priced_sort/"

    elif misc == "ONLY NEW":
        initial_url = "https://www.zillow.com/homes/for_sale/" + neighborhood\
                      + "-Chicago-IL/1_days/"

    print(initial_url)

    url_loc, soup = parse_url(initial_url)
    time.sleep(2)

    page_counter, tot_num = find_num_pages(soup, initial_url, misc)
 
    if tot_num == 0:
        print("returning string yay")
        return (0, 0)

    if page_counter == 1:
        print("one page of results")
        if len(url_loc) > 0 and 1 not in url_loc:
            url_loc = get_house_info(url_loc)          
            return (url_loc, neighborhood)
        else:
            while True:
                print("returned empty, trying again")
                time.sleep(2)
                url_loc, soup = parse_url(initial_url)
                if 1 in url_loc:
                    print("too much missing data, could not return results")
                    return None
                elif 1 not in url_loc and len(url_loc) > 0:
                    url_loc = get_house_info(url_loc)
                    return (url_loc, neighborhood)
                else:
                    url_loc = {}
                    return url_loc

    elif page_counter == 2:
        print("two pages of results, going on to second page")
        next_url = initial_url + (str(page_counter) + "_p/")
        print(next_url)
        next_url_loc, soup = parse_url(next_url)
        if len(next_url_loc) > 0 and 1 not in next_url_loc:
            url_loc.update(next_url_loc)
            url_loc = get_house_info(url_loc)
            return (url_loc, neighborhood)
        else:
            while True:
                print("returned empty, trying again")
                time.sleep(2)
                next_url_loc, soup = parse_url(next_url)
                if 1 in next_url_loc:
                    print("too much missing data, could not return results")
                    return None
                elif len(next_url_loc) > 0 and 1 not in next_url_loc:
                    url_loc.update(next_url_loc)
                    url_loc = get_house_info(url_loc)
                    return (url_loc, neighborhood)
                else:
                    url_loc = {}
                    return url_loc

    else:
        print("preparing to loop through", page_counter, "pages")
        for p in range(2, page_counter + 1):
            next_url = initial_url + (str(p) + "_p/")
            print(next_url)
            next_url_loc, soup = parse_url(next_url)
            if len(next_url_loc) == 0:
                print("returned empty, trying again")
                time.sleep(2)
                next_url_loc, soup = parse_url(next_url)
                if len(next_url_loc) > 0:
                    url_loc.update(next_url_loc)
                else:
                    return url_loc 
            elif 1 in next_url_loc:
                print("too much missing data, could not return results for this page")
                continue
            elif len(next_url_loc) > 0 and 1 not in next_url_loc:                   
                url_loc.update(next_url_loc)
                time.sleep(2)

    url_loc = {url:values for url, values in url_loc.items() if url != 1}

    url_loc = get_house_info(url_loc)

    url_loc = {url:values for url, values in url_loc.items() if values[2] != '$'}

    return (url_loc, neighborhood)


def get_house_info(url_loc):
    '''
    Gets the price, number of beds, and number of baths in a house 
    returned by the search results.

    Inputs:
        url_loc: (dict) The dictionary mapping house urls to their 
                 latitude/longitude locations.

    Outputs:
        url_loc: (dict) The updated dictionary that adds the price, 
                 number of beds, and number of baths of each house 
                 to the dictionary values.
    '''

    for url in url_loc.keys():
        request_headers = {'accept': 'text/html,application/xhtml+xml,\
                            application/xml;q=0.9,image/webp,image/apng\
                            ,*/*;q=0.8',
                           'accept-encoding': 'gzip, deflate, br',
                           'accept-language': 'en-US,en;q=0.8',
                           'upgrade-insecure-requests': '1',
                           'user-agent': 'Mozilla/5.0 (Windows NT 10.0; \
                            Win64; x64) AppleWebKit/537.36 (KHTML, \
                            like Gecko) Chrome/61.0.3163.100 Safari/537.36'}

        request_headers_1 = {'accept':'text/html,application/xhtml+xml,\
                              application/xml;q=0.9,image/webp,*/*;q=0.8',
                             'accept-encoding':'gzip, deflate, sdch, br',
                             'accept-language':'en-GB,en;q=0.8,en-US;q=0.6,\
                              ml;q=0.4',
                             'cache-control':'max-age=0',
                             'upgrade-insecure-requests':'1',
                             'user-agent':'Mozilla/5.0 (X11; Linux x86_64) \
                              AppleWebKit/537.36 (KHTML, like Gecko) \
                              Chrome/56.0.2924.87 Safari/537.36'}

        with requests.Session() as a:
            response = a.get(url, headers=request_headers)
            time.sleep(1)

        soup = BeautifulSoup(response.content, "lxml")

        metas = str(soup.find_all("meta"))

        if len(metas) == 2:
            print("switching headers")
            with requests.Session() as a:
                response = a.get(url, headers = request_headers_1)
                time.sleep(1)
            soup = BeautifulSoup(response.content, "lxml")
        title = str(soup.find_all("meta")[2])
 
        if "$" in title:
            if "sqft" in title:
                price_index = title.index("$")
                size_index = title.index("sqft")

                info = title[price_index:size_index+4].split()
        
                price = info[0]
                beds = info[1]
                baths = info[3]

                if beds == 'bed,':
                    beds = 'beds'

                if baths == 'sqft':
                    baths = 'baths'

                if baths == 'bath,':
                    baths = 'baths'

        elif "$" not in title:
            price = "$"
            beds = "beds"
            baths = "baths"

        new_info = [price, beds, baths]
        print(new_info)

        for i in new_info:
            url_loc[url].append(i)  

    return url_loc


def get_only_new_listings(area, beds=0, baths=0, price_min=0, price_max=1000000000):
    '''
    Returns the dictionary mapping urls of houses put on Zillow in the 
    past day in a neighborhood to their latitude/longitude locations, price, 
    number of beds and number of baths.
    '''

    return get_all_results(0, 0, 0, 0, area, 'ONLY NEW')


def was_recently_sold(url):
    '''
    Returns a boolean that indicates whether or not a house has 
    been recently sold.

    Inputs:
        url: (string) The url of a house.
    
    Outputs:
        True if the house has been recently sold, and False if
        it has not been recently sold.
    '''

    request_headers = {'accept': 'text/html,application/xhtml+xml,application\
                        /xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                       'accept-encoding': 'gzip, deflate, br',
                       'accept-language': 'en-US,en;q=0.8',
                       'upgrade-insecure-requests': '1',
                       'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; \
                        x64) AppleWebKit/537.36 (KHTML, like Gecko) \
                        Chrome/61.0.3163.100 Safari/537.36'}

    with requests.Session() as a:
        response = a.get(url, headers=request_headers)

    time.sleep(1)

    soup = BeautifulSoup(response.content, "lxml")

    return str(soup.find_all("meta")[27])[15:28] == "Recently sold"


def get_all_chicago_housing():
    '''
    Returns a dictionary of the urls all of the for sale houses in Chicago 
    mapped to their respective information.
    '''

    return get_all_results(0, 0, 0, 1000000000, "", "sale")


