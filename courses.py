### CS122, Winter 2018: Course search engine: search
###
### Kyle Pinder

from math import radians, cos, sin, asin, sqrt
import sqlite3
import os


# Use this filename for the database
DATA_DIR = os.path.dirname(__file__)
DATABASE_FILENAME = os.path.join(DATA_DIR, 'course-info.db')


def find_courses(args_from_ui):
    '''
    Takes a dictionary containing search criteria and returns courses
    that match the criteria.  The dictionary will contain some of the
    following fields:

      - dept a string
      - day is array with variable number of elements
           -> ["'MWF'", "'TR'", etc.]
      - time_start is an integer in the range 0-2359
      - time_end is an integer an integer in the range 0-2359
      - enroll is an integer
      - walking_time is an integer
      - building ia string
      - terms is a string: "quantum plato"]

    Returns a pair: list of attribute names in order and a list
    containing query results.
    '''

    search_header = []
    search_results = []

    terms_dict = \
    {"attributes": ["courses.dept", "courses.course_num", "courses.title"],\
     "tables": ["courses", "catalog_index", "sections"],\
     "join_cols": ["courses.course_id = catalog_index.course_id",\
     "courses.course_id = sections.course_id"],\
     "value_column": "catalog_index.word", "value_operator": "=",\
     "value_join": " OR "}

    dept_dict = \
    {"attributes": ["courses.dept", "courses.course_num", "courses.title"],\
     "tables": ["courses"], "join_cols": [], "value_column": "courses.dept",\
     "value_operator": "=", "value_join": " AND "}

    day_dict = \
    {"attributes": ["courses.dept", "courses.course_num",\
     "sections.section_num", "meeting_patterns.day",\
     "meeting_patterns.time_start", "meeting_patterns.time_end"],\
     "tables": ["courses", "sections", "meeting_patterns"],\
     "join_cols": ["courses.course_id = sections.course_id",\
     "sections.meeting_pattern_id = meeting_patterns.meeting_pattern_id"],\
     "value_column": "meeting_patterns.day", "value_operator": "=",\
     "value_join": " OR "}

    time_start_dict = \
    {"attributes": ["courses.dept", "courses.course_num",\
     "sections.section_num", "meeting_patterns.day",\
     "meeting_patterns.time_start", "meeting_patterns.time_end"],\
     "tables": ["courses", "sections", "meeting_patterns"],\
     "join_cols": ["courses.course_id = sections.course_id",\
     "sections.meeting_pattern_id = meeting_patterns.meeting_pattern_id"],\
     "value_column": "meeting_patterns.time_start", "value_operator": ">=",\
     "value_join": ""}

    time_end_dict = \
    {"attributes": ["courses.dept", "courses.course_num",\
     "sections.section_num", "meeting_patterns.day",\
     "meeting_patterns.time_start", "meeting_patterns.time_end"],\
     "tables": ["courses", "sections", "meeting_patterns"],\
     "join_cols": ["courses.course_id = sections.course_id",\
     "sections.meeting_pattern_id = meeting_patterns.meeting_pattern_id"],\
     "value_column": "meeting_patterns.time_end", "value_operator": "<=",\
     "value_join": ""}

    walking_time_dict = \
    {"attributes": ["courses.dept", "courses.course_num",\
     "sections.section_num", "meeting_patterns.day",\
     "meeting_patterns.time_start", "meeting_patterns.time_end",\
     "sections.building_code",\
     "time_between(a.lon, a.lat, b.lon, b.lat) AS walking_time"],\
     "tables": ["courses", "sections", "meeting_patterns",\
     "gps AS a", "gps AS b"],\
     "join_cols": ["courses.course_id = sections.course_id",\
     "sections.meeting_pattern_id = meeting_patterns.meeting_pattern_id",\
     "sections.building_code = a.building_code"],\
     "value_column": "walking_time", "value_operator": "<=", "value_join": ""}

    building_dict = \
    {"attributes": ["courses.dept", "courses.course_num",\
     "sections.section_num", "meeting_patterns.day",\
     "meeting_patterns.time_start", "meeting_patterns.time_end",\
     "sections.building_code",\
     "time_between(a.lon, a.lat, b.lon, b.lat) AS walking_time"],\
     "tables": ["courses", "sections", "meeting_patterns",\
     "gps AS a", "gps AS b"],\
     "join_cols": ["courses.course_id = sections.course_id",\
     "sections.meeting_pattern_id = meeting_patterns.meeting_pattern_id",\
     "sections.building_code = a.building_code"],\
     "value_column": "b.building_code", "value_operator": "=",\
     "value_join": ""}

    enroll_lower_dict = \
    {"attributes": ["courses.dept", "courses.course_num",\
     "sections.section_num", "meeting_patterns.day",\
     "meeting_patterns.time_start", "meeting_patterns.time_end",\
     "sections.enrollment"],\
     "tables": ["courses", "sections", "meeting_patterns"],\
     "join_cols": ["courses.course_id = sections.course_id",\
     "sections.meeting_pattern_id = meeting_patterns.meeting_pattern_id"],\
     "value_column": "sections.enrollment", "value_operator": ">=",\
     "value_join": ""}

    enroll_upper_dict = \
    {"attributes": ["courses.dept", "courses.course_num",\
     "sections.section_num", "meeting_patterns.day",\
     "meeting_patterns.time_start", "meeting_patterns.time_end",\
     "sections.enrollment"],\
     "tables": ["courses", "sections", "meeting_patterns"],\
     "join_cols": ["courses.course_id = sections.course_id",\
     "sections.meeting_pattern_id = meeting_patterns.meeting_pattern_id"],\
     "value_column": "sections.enrollment", "value_operator": "<=",\
     "value_join": ""}

    parameters_dict = \
    {"terms": terms_dict, "dept": dept_dict, "day": day_dict,\
     "time_start": time_start_dict, "time_end": time_end_dict,\
     "walking_time": walking_time_dict, "building": building_dict,\
     "enroll_lower": enroll_lower_dict, "enroll_upper": enroll_upper_dict}

    select_list = [] 
    table_list = []
    join_cols_list = []
    where_list = []
    search_arg_list = []   

    arg_keys = args_from_ui.keys()

    for arg in arg_keys:
        if arg in parameters_dict:
            select_list += parameters_dict[arg]["attributes"]
            table_list += parameters_dict[arg]["tables"]
            join_cols_list += parameters_dict[arg]["join_cols"]
            val_col = parameters_dict[arg]["value_column"]
            val_op = parameters_dict[arg]["value_operator"]
            val_join = parameters_dict[arg]["value_join"]
            arg_values = args_from_ui[arg]

            if arg == "terms":
                arg_values = arg_values.split()

            search_values = []

            if arg_values and type(arg_values) is list:
                for a in arg_values:
                    search_str = val_col + " " + val_op + " ?"
                    search_values.append(search_str)
                    search_arg_list.append(a)

            else:
                search_str = val_col + " " + val_op + " ?"
                search_values.append(search_str)
                search_arg_list.append(arg_values)

            if len(search_values) > 1:
                where_string = " (" + val_join.join(search_values)  + ")"
                where_list.append(where_string)

            else:
                where_list.append(val_join.join(search_values))
            

    select_list = ", ".join(remove_duplicates(select_list))
    table_list = " JOIN ".join(remove_duplicates(table_list))
    join_cols_list = " AND ".join(remove_duplicates(join_cols_list))
    where_list = " AND ".join(where_list)
    val_term = ""

    if "terms" in args_from_ui:
        val_term = " GROUP BY catalog_index.course_id, sections.section_num\
                   HAVING COUNT(catalog_index.course_id) = " + \
                   str(len(args_from_ui["terms"].split()))

    query_string = "SELECT " + select_list + " FROM " + table_list + " ON " +\
                   join_cols_list + " WHERE " + where_list + val_term

    db = sqlite3.connect("course-info.db")
    c = db.cursor()

    if "walking_time" in args_from_ui and "building" in args_from_ui:
        db.create_function("time_between", 4, compute_time_between)

    r = c.execute(query_string, search_arg_list)

    search_results = r.fetchall()

    if search_results:
        search_header = get_header(c)
   
    db.close()

    return (search_header, search_results)


#https://stackoverflow.com/questions/480214/how-do-you-remove-duplicates-
#from-a-list-in-whilst-preserving-order

def remove_duplicates(query_list):
    '''
    Takes a list of queries and removes any potential duplicates.

    Inputs:
        query_list: (list) A list of queries

    Returns:
        The query list without duplicates.
    '''

    q_set = set()
    q_set_add = q_set.add
    return [x for x in query_list if not (x in q_set or q_set_add(x))]


########### auxiliary functions #################
########### do not change this code #############

def compute_time_between(lon1, lat1, lon2, lat2):
    '''
    Converts the output of the haversine formula to walking time in minutes
    '''
    meters = haversine(lon1, lat1, lon2, lat2)

    # adjusted downwards to account for manhattan distance
    walk_speed_m_per_sec = 1.1
    mins = meters / (walk_speed_m_per_sec * 60)

    return mins


def haversine(lon1, lat1, lon2, lat2):
    '''
    Calculate the circle distance between two points
    on the earth (specified in decimal degrees)
    '''
    # convert decimal degrees to radians
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

    # haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * asin(sqrt(a))

    # 6367 km is the radius of the Earth
    km = 6367 * c
    m = km * 1000
    return m


def get_header(cursor):
    '''
    Given a cursor object, returns the appropriate header (column names)
    '''
    desc = cursor.description
    header = ()

    for i in desc:
        header = header + (clean_header(i[0]),)

    return list(header)


def clean_header(s):
    '''
    Removes table name from header
    '''
    for i, _ in enumerate(s):
        if s[i] == ".":
            s = s[i + 1:]
            break

    return s


########### some sample inputs #################

EXAMPLE_0 = {"time_start": 930,
             "time_end": 1500,
             "day": ["MWF"]}

EXAMPLE_1 = {"dept": "CMSC",
             "day": ["MWF", "TR"],
             "time_start": 1030,
             "time_end": 1500,
             "enroll_lower": 20,
             "terms": "computer science"}
