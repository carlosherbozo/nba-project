#! /usr/bin/env python
'''This module handles the registrar server'''
from argparse import ArgumentParser
import sys
from app import app, db

def main():
    '''Parses args and starts regserver'''
    parser = ArgumentParser(description='The registrar application')
    parser.add_argument('port', help='the port at which the server should listen')
    args = parser.parse_args()
    try:
        port = int(args.port)
    except ValueError:
        print('Invalid port:', args.port, file=sys.stderr)
        sys.exit(1)

    with app.app_context():
        try:
            db.create_all()
            app.run(host='0.0.0.0', port=port, debug=True)
        except Exception as ex:
            print(ex, file=sys.stderr)
            sys.exit(1)

if __name__ == '__main__':
    main()