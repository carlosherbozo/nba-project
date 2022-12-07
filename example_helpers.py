'''helpers for regapp'''

from sqlite3 import Cursor, connect, Row
from contextlib import closing
from flask import Response

#Constants
#Map command line arguments to col column_names
#arg_abbrev: [is_optional_arg, arg_name, arg_descrip]
reg_arg_details = {
    'd': [
        True,
        'deptname show only those classes whose department code contains dept',
        'deptname'
        ],
    's': [
        True,
        'subjectcode show only those classes whose subjectcode contains subject',
        'subjectcode'
        ],
    'n': [
        True,
        'num show only those classes whose course number contains num',
        'coursenum'
        ],
    't': [
        True,
        'title show only those classes whose course title contains title',
        'title'
        ]
    }

def execute_query(cursor: Cursor, stmt_str: str, variables: tuple):
    '''Executes stmt_str query using cursor. Creates table with formatting from format_str.'''
    cursor.execute(stmt_str, variables)
    #Fetch all rows
    data = cursor.fetchall()
    return data

def handle_dict(params):
    '''This function handles client requests when the requested item is a dictionary'''
    # SQLite Query
    db_url = 'file:reg.sqlite?mode=ro'
    data = params.copy()
    if isinstance(data, dict):
        # format dict values and delete empty args
        for key in list(data.keys()):
            if data[key] is not None and data[key] != '':
                data[key] = '%' + data[key] + '%'
            else:
                del data[key]
    with connect(db_url, isolation_level=None, uri=True) as connection:
        # Create row factory
        connection.row_factory = Row
        with closing(connection.cursor()) as cursor:
            # Setup SQL query with proper filters
            stmt_str = "SELECT DISTINCT crn AS crns, deptname, subjectcode "
            stmt_str += "AS subject, coursenum AS num, title "
            stmt_str += "FROM ((courses NATURAL JOIN departments) "
            stmt_str += "NATURAL JOIN sections) "
            filters = []
            vals = []

            for key in data.keys():
                filters.append(f"\"{reg_arg_details[key][2]}\" LIKE ? ")
                vals.append(data[key])
            if len(filters) != 0:
                stmt_str += ("WHERE " + " AND ".join(filters))
            stmt_str += "GROUP BY courseid "
            stmt_str += "ORDER BY deptname ASC, coursenum ASC, crns ASC"

            #Execute SQL query
            return execute_query(cursor, stmt_str, vals)

def handle_crn(crn):
    '''Handles CRN requests from client. Routes to ????'''

    crn = tuple([crn])

    # SQLite Query
    db_url = 'file:reg.sqlite?mode=ro'

    with connect(db_url, isolation_level=None, uri=True) as connection:
        connection.row_factory = Row
        with closing(connection.cursor()) as cursor:
            list_of_tables = []
            stmt_str1 = "SELECT deptname, subjectcode, coursenum "
            stmt_str1 += "FROM ((courses NATURAL JOIN departments) NATURAL JOIN sections) "
            stmt_str1 += "WHERE crn = ?"
            list_of_tables.append(execute_query(cursor, stmt_str1, crn))
            #Table 2
            stmt_str2 = "SELECT title FROM (courses NATURAL JOIN sections) "
            stmt_str2 += "WHERE crn = ?"
            list_of_tables.append(execute_query(cursor, stmt_str2, crn))
            #Table 3
            stmt_str3 = "SELECT descrip FROM (courses NATURAL JOIN sections) "
            stmt_str3 += "WHERE crn = ?"
            list_of_tables.append(execute_query(cursor, stmt_str3, crn))
            #Table 4
            stmt_str4 = "SELECT prereqs FROM (courses NATURAL JOIN sections) "
            stmt_str4 += "WHERE crn = ?"
            list_of_tables.append(execute_query(cursor, stmt_str4, crn))
            #Table 5
            stmt_str5 = "SELECT sectionnumber, crn, "
            stmt_str5 += "GROUP_CONCAT(timestring || ' @ ' || locstring, '|') "
            stmt_str5 += "AS meetinginfo FROM "
            stmt_str5 += "(courses NATURAL JOIN sections NATURAL JOIN meetings) "
            stmt_str5 += "WHERE courseid = "
            stmt_str5 += "(SELECT courseid FROM courses NATURAL JOIN sections WHERE crn = ?) "
            stmt_str5 += "GROUP BY sectionnumber, crn ORDER BY sectionnumber ASC, crn ASC"
            list_of_tables.append(execute_query(cursor, stmt_str5, crn))
            #Table 6
            stmt_str6 = "SELECT subjectcode, coursenum "
            stmt_str6 += "FROM courses WHERE courseid IN "
            stmt_str6 += "(SELECT secondarycourseid FROM crosslistings "
            stmt_str6 += "WHERE primarycourseid = (SELECT courseid FROM sections WHERE crn = ?)) "
            stmt_str6 += "ORDER BY subjectcode ASC, coursenum ASC"
            list_of_tables.append(execute_query(cursor, stmt_str6, crn))
            #Table 7
            stmt_str7 = "SELECT profname AS professors "
            stmt_str7 += "FROM (courses NATURAL JOIN (coursesprofs NATURAL JOIN "
            stmt_str7 += "(profs NATURAL JOIN sections))) "
            stmt_str7 += "WHERE crn = ?"
            stmt_str7 += "ORDER BY profname ASC"
            list_of_tables.append(execute_query(cursor, stmt_str7, crn))

            return list_of_tables

def set_cookies(res: Response, parameters: dict):
    '''Sets cookies after query'''
    for k in parameters.keys():
        res.set_cookie(reg_arg_details[k][2], parameters[k])
    return res
