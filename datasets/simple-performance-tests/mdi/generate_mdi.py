#!/usr/bin/env python3
import arango
import os
import argparse

ARANGO_HOSTS = os.environ['ARANGO_HOSTS']
ARANGO_USERNAME = os.environ['ARANGO_USERNAME']
ARANGO_PASSWORD = os.environ['ARANGO_PASSWORD']
ARANGO_DATABASE = os.environ['ARANGO_DATABASE']

def generate(num_docs):
    client = arango.ArangoClient(hosts=ARANGO_HOSTS)

    print(f"Running mdi generator script - generating {num_docs} documents in {ARANGO_HOSTS} database: {ARANGO_DATABASE}")

    # create mdi database
    db = client.db(ARANGO_DATABASE, username=ARANGO_USERNAME, password=ARANGO_PASSWORD)

    # create collection
    if not db.has_collection('mdi'):
        db.create_collection('mdi')
    c = db.collection('mdi')
    c.truncate()

    c.add_index({'type': 'mdi', 'name': 'mdi', 'fields': ["x", "y"], 'fieldValueTypes': "double"})

    # insert documents
    db.aql.execute("""
        FOR i IN 1..@num_docs
            LET x = (i - 500) / 10
            LET y = x + 0.5
            INSERT {x, y, i} INTO @@c
    """, bind_vars={"num_docs": num_docs, "@c": c.name})

    print("mdi generation done")


def main():
    argparser = argparse.ArgumentParser()
    argparser.add_argument('--num-docs', type=int, default=1000000)
    args = argparser.parse_args()
    generate(args.num_docs)

if __name__ == '__main__':
    main()
