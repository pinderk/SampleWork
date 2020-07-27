# CS122: Course Search Engine Part 1
#
# Kyle Pinder
#

import re
import util
import bs4
import queue
import json
import sys
import csv

INDEX_IGNORE = set(['a', 'also', 'an', 'and', 'are', 'as', 'at', 'be',
                    'but', 'by', 'course', 'for', 'from', 'how', 'i',
                    'ii', 'iii', 'in', 'include', 'is', 'not', 'of',
                    'on', 'or', 's', 'sequence', 'so', 'social', 'students',
                    'such', 'that', 'the', 'their', 'this', 'through', 'to',
                    'topics', 'units', 'we', 'were', 'which', 'will', 'with',
                    'yet'])


def clean_url(url, limiting_domain, parent_url):
    '''
    Cleans the given url, if necessary.

    Inputs:
        url: (string) A url
        limiting_domain: (string) The limiting domain of the url.
        parent_url: (string) The partent url if the given url is incomplete.

    Outputs:
        The cleaned url if it is ok to follow, and None otherwise.  
    '''

    c_url = util.remove_fragment(url)
    c_url = util.convert_if_relative_url(parent_url, c_url)
    
    if util.is_url_ok_to_follow(c_url, limiting_domain):
        return c_url

    return None


def find_course_info(soup, coursemap, course_dict):
    '''
    Creates the dictionary mapping the course information to the course id.

    Inputs:
        soup: The html text organized into soup.
        coursemap: (dictionary) The dictionary mapping coursenames to their 
                   id number.
        course_dict: (dictionary) The dictionary used to update the returned
                     dictionary through each iteration of the loop.

    Outputs:
        The dictionary mapping course information to the course id.
    '''

    courses = soup.find_all("div", class_="courseblock main")

    new_dict = {k:v for k, v in course_dict.items()}

    for course in courses:
        course_title = course.find("p", class_="courseblocktitle").text
        course_description = course.find("p", class_="courseblockdesc").text
        course_text = course_title + " " + course_description
        subseq_list = util.find_sequence(course)
        if subseq_list:
            for subseq in subseq_list:
                subseq_title = subseq.find\
                ("p", class_="courseblocktitle").text
                subseq_description = subseq.find\
                ("p", class_="courseblockdesc").text
                subseq_text = subseq_title + " " + subseq_description\
                 + " " + course_text
                sub_text_list = clean_text(subseq_text)
                subseq_id = get_course_identifier(subseq_title, coursemap)
                for s in sub_text_list:
                    if s not in new_dict:
                        new_dict[s] = []
                    if subseq_id not in new_dict[s]:
                        new_dict[s].append(subseq_id) 
 
        else:
            text_list = clean_text(course_text)
            course_id = get_course_identifier(course_title, coursemap)
            for t in text_list:
                if t not in new_dict:
                    new_dict[t] = []
                if course_id not in new_dict[t]:
                    new_dict[t].append(course_id)  

    return new_dict 
             

def get_course_identifier(title, coursemap):
    '''
    Finds the course id number for each course title.

    Inputs:
        title: (string) The title of the course.
        coursemap: (dictionary) The dictionary mapping the course 
                   titles to the course id number.

    Outputs:
        The course id number.
    '''

    #https://exceptionshub.com/python-removing-xa0-from-string.html
    new_title = title.replace("&#160;", " ").replace(u"\xa0", u" ")

    new_title = new_title.split(".")[0]

    course_id = coursemap[new_title]

    return course_id


def clean_text(raw_text):
    '''
    Cleans the text in the course description and title.

    Inputs:
        raw_text: (string) A string of characters.

    Outputs:
        The cleaned list of characters.
    '''

    raw_text = raw_text.replace("&#160;", " ").replace("u\xa0", u" ").lower()

    word_list = []
    clean_word_list = []

    for term in re.findall("[a-zA-Z]\w*", raw_text):
        word_list.append(term)

    for word in word_list:
        if len(word) >= 1 and word not in INDEX_IGNORE and word not in \
        clean_word_list:
            clean_word_list.append(word)

    return clean_word_list


def create_dictionary(num_pages_to_crawl, course_map_filename, starting_url,
                      limiting_domain):
    '''
    Creates the dictionary mapping course id numbers to the words in the
    course titles and descriptions.

    Inputs:
        num_pages_to_crawl: (int) The number of pages to process
                            during the crawl.
        course_map_filename: (string) The name of the JSON file that contains
                             the mapping of course codes to course ids.
        starting_url: (string) The url of the first page that the
                      crawler visits.
        limiting_domain: (string) The limiting domain of the url.

    Outputs:
        The dictionary mapping course id numbers to the words in the course 
        titles and descriptions.
    '''

    with open(course_map_filename) as json_file:
        coursemap = json.load(json_file)

    url_list = []
    url_queue = queue.Queue()
    num_pages = 0
    course_dict = {}
    process_dict = {}

    starting_url = clean_url(starting_url, limiting_domain, parent_url=None)

    if starting_url:
        url_queue.put(starting_url)

    while num_pages < num_pages_to_crawl and not url_queue.empty():
        num_pages += 1
        next_url = url_queue.get()
        if next_url and next_url not in url_list:
            request = util.get_request(next_url)
            if request:
                request_url = util.get_request_url(request)
                if request_url and request_url not in url_list:
                    url_list.append(next_url)
                    if request_url not in url_list:
                        url_list.append(request_url)
                    html_text = util.read_request(request)
                    soup = bs4.BeautifulSoup(html_text, "html5lib")
                    process_dict.update(find_course_info(soup, coursemap,\
                    course_dict))
                    if process_dict:               
                        course_dict.update(process_dict)
                    href_list = soup.find_all("a", href=True)
                    for h in href_list:
                        h_url = h['href']
                        h_url = clean_url(h_url, limiting_domain, request_url)        
                        if h_url:
                            url_queue.put(h_url)

    return course_dict 


def create_csv(index_dict, index_filename):
    '''
    Creates the CSV file of the course id numbers and words that they match.

    Inputs:
        index_dict: (dictionary) The dictionary mapping course id numbers to 
                    the words in the course title and description.
        index_filename: (string) The filename of the new CSV file.

    Outputs:
        No explicit output; creates the CSV file.
    '''
    
    with open(index_filename, "w") as csv_file:
        dict_writer = csv.writer(csv_file, delimiter="|") 
        for term in index_dict.keys():
            for course_id in index_dict[term]:
                dict_writer.writerow([course_id, term])

            
def go(num_pages_to_crawl, course_map_filename, index_filename):
    '''
    Crawl the college catalog and generate a CSV file with an index.

    Inputs:
        num_pages_to_crawl: (int) The number of pages to process 
                            during the crawl.
        course_map_filename: (string) The name of a JSON file that contains 
                             the mapping of course codes to course identifiers
        index_filename: Istring) The name for the CSV of the index.

    Outputs:
        CSV file of the index
    '''

    starting_url = ("http://www.classes.cs.uchicago.edu/archive/2015/winter"
                    "/12200-1/new.collegecatalog.uchicago.edu/index.html")
    limiting_domain = "classes.cs.uchicago.edu"

    index_dict = create_dictionary(num_pages_to_crawl, course_map_filename, \
                 starting_url, limiting_domain)

    create_csv(index_dict, index_filename)


if __name__ == "__main__":
    usage = "python3 crawl.py <number of pages to crawl>"
    args_len = len(sys.argv)
    course_map_filename = "course_map.json"
    index_filename = "catalog_index.csv"
    if args_len == 1:
        num_pages_to_crawl = 1000
    elif args_len == 2:
        try:
            num_pages_to_crawl = int(sys.argv[1])
        except ValueError:
            print(usage)
            sys.exit(0)
    else:
        print(usage)
        sys.exit(0)

    go(num_pages_to_crawl, course_map_filename, index_filename)
