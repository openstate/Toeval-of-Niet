#!/usr/bin/env python
# encoding: utf-8
"""
untitled.py

Created by Breyten Ernsting on 2012-06-14.
Copyright (c) 2012 __MyCompanyName__. All rights reserved.
"""

import sys
import getopt
import csv, codecs, cStringIO, json

from restkit import Resource, BasicAuth

# import requests

help_message = '''
The help message goes here.
'''

class UTF8Recoder:
    """
    Iterator that reads an encoded stream and reencodes the input to UTF-8
    """
    def __init__(self, f, encoding):
        self.reader = codecs.getreader(encoding)(f)

    def __iter__(self):
        return self

    def next(self):
        return self.reader.next().encode("utf-8")


class UnicodeReader:
    """
    A CSV reader which will iterate over lines in the CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        f = UTF8Recoder(f, encoding)
        self.reader = csv.reader(f, dialect=dialect, **kwds)

    def next(self):
        row = self.reader.next()
        return [unicode(s, "utf-8") for s in row]

    def __iter__(self):
        return self

class Usage(Exception):
    def __init__(self, msg):
        self.msg = msg


def _post_request(url_path, payload):
    auth = BasicAuth('breyten','0116ffc25e28b40c883b6ae8a46a9bd49373e7c5')
    res = Resource('http://toevalofniet.com', filters=[auth])
    headers = ({'Accepted': 'application/json', 'Content‐Type': 'application/json'})
    result = res.post(path='/api/1.0/' + url_path + '/', payload=payload, headers=headers)
    return result

def _get_request(url_path):
    auth = BasicAuth('breyten','0116ffc25e28b40c883b6ae8a46a9bd49373e7c5')
    res = Resource('http://toevalofniet.com', filters=[auth])
    headers = ({'Accepted': 'application/json', 'Content‐Type': 'application/json'})
    result = res.get(path='/api/1.0/' + url_path + '/', headers=headers)
    return result

def add_entity(name, entity_type):
    res = _post_request('entity', {'name': name, 'entity_type': entity_type})
    return res

def get_entity_types():
    response = _get_request('entity_type')
    result = json.loads(response.body_string())
    types = {}
    for entity_type in result['objects']:
        types[entity_type['name']] = entity_type[u'resource_uri']
    return types

def get_relation_types():
    response = _get_request('relation_type')
    result = json.loads(response.body_string())
    types = {}
    for entity_type in result['objects']:
        types[entity_type['description']] = entity_type[u'resource_uri']
    return types
    
def run(input_file, verbose=False):
    f = codecs.open(input_file, "UTF-8")
    entity_types = []
    relation_types = []
    entities = []
    i = 0
    entity_types = get_entity_types()
    relation_types = get_relation_types()
    entities = {}
    rows = []
    for r in UnicodeReader(f):
        if i > 0:
            entities[r[1]] = r[3]
            entities[r[2]] = r[-1]
            data = {
                'entity1': {
                    'name': r[1],
                    'type': r[3]
                },
                'entity2': {
                    'name': r[2],
                    'type': r[-1]
                },
                'relation': {
                    'startdate': r[7],
                    'enddate': r[8],
                    'private': False,
                    'publication_date': r[0],
                },
                'relation_type': {
                    'description': r[5],
                    'description_reversed': r[5]
                }
            }
            print data
            rows.append(data)
        i = i + 1
    for entity in entities:
        print entity
        add_entity(entity, entity_types[entities[entity]])

def main(argv=None):
    if argv is None:
        argv = sys.argv
    try:
        try:
            opts, args = getopt.getopt(argv[1:], "hi:v", ["help", "input="])
        except getopt.error, msg:
            raise Usage(msg)
    
        # option processing
        verbose = False
        for option, value in opts:
            if option == "-v":
                verbose = True
            if option in ("-h", "--help"):
                raise Usage(help_message)
            if option in ("-i", "--input"):
                input_file = value
        run(input_file, verbose)

    except Usage, err:
        print >> sys.stderr, sys.argv[0].split("/")[-1] + ": " + str(err.msg)
        print >> sys.stderr, "\t for help use --help"
        return 2


if __name__ == "__main__":
    sys.exit(main())
