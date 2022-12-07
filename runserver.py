#! /usr/bin/env python
'''This module handles the registrar server'''
from argparse import ArgumentParser
import sys
from app import app, db

def main():
    with app.app_context():
        try:
            db.create_all()
            app.run(host='0.0.0.0', port=80, debug=True)
        except Exception as ex:
            print(ex, file=sys.stderr)
            sys.exit(1)

if __name__ == '__main__':
    main()