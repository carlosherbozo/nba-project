#!/usr/bin/env python3
'''This is the registrar application module'''
from flask import Flask, make_response, render_template, request
from example_helpers import handle_dict, handle_crn, set_cookies

#-----------------------------------------------------------------------

app = Flask(__name__)

#-----------------------------------------------------------------------

@app.route('/', methods=['GET'])
@app.route('/search', methods=['GET'])
def index():
    '''The index page with search results (if any)'''
    deptname = request.args.get('deptname')
    coursenum = request.args.get('coursenum')
    subject = request.args.get('subject')
    title = request.args.get('title')
    if all(item is None for item in [deptname, coursenum, subject, title]):
        deptname = request.cookies.get('deptname')
        coursenum = request.cookies.get('coursenum')
        subject = request.cookies.get('subject')
        title = request.cookies.get('title')
    if any(item is not None for item in [deptname, coursenum, subject, title]):
        parameters = {
            "d": deptname if deptname else '',
            "n": coursenum if coursenum else '',
            "s": subject if subject else '',
            "t": title if title else ''
        }
        data_access_response = handle_dict(parameters)
        if len(data_access_response) == 0:
            error = "No results, check your search parameters or redefine your search"
        else:
            error = ''
        html = render_template('index.html', params=parameters, \
            data = data_access_response, error = error)
        response = set_cookies(make_response(html), parameters)
    else:
        html = render_template('index.html')
        response = make_response(html)
    return response

@app.route('/details', methods=['GET'])
def details():
    '''This page provides more info for a specific course'''
    crn = request.args.get("crn")
    try:
        data_access_response = handle_crn(crn)
        html = render_template('details.html', data = data_access_response, error = None)
        response = make_response(html)
        return response
    except:
        if crn == '' or crn is None:
            error = "Error: missing crn in details request"
        else:
            error = f"Error: no class with crn {crn} exists"
        html = render_template('details.html', data = None, error = error)
        response = make_response(html)
        return response
