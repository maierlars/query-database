#!/usr/bin/env python3
import arango
import os
import argparse
import random

ARANGO_HOSTS = os.environ['ARANGO_HOSTS'].split(',')
ARANGO_USER = os.environ['ARANGO_USER']
ARANGO_PASSWORD = os.environ['ARANGO_PASSWORD']
ARANGO_DATABASE = os.environ['ARANGO_DATABASE']

def generate_random_string(length):
    ''.join(choice(ascii_uppercase) for i in range(length))

def generate(num_docs, num_edges, batch_size):
    client = arango.ArangoClient(hosts=ARANGO_HOSTS)

    ddb = client.db()

    ddb.delete_database("hop", ignore_missing=True)
    ddb.create_database("hop")

    # create hopgraph database
    db = client.db(ARANGO_DATABASE, username=ARANGO_USER, password=ARANGO_PASSWORD)
    hopgraph = db.create_graph("hopgraph")

    # Create an edge definition (relation) for the graph.
    E = hopgraph.create_edge_definition(
        edge_collection="E",
        from_vertex_collections=["A"],
        to_vertex_collections=[f"B{i}" for i in range(1,10)]
    )
    F = hopgraph.create_edge_definition(
        edge_collection="F",
        # TODO: check whether this is intentional (that the graph only defines
        # itself to be between B1 and all C{i}
        from_vertex_collections=["B1"],
        to_vertex_collections=[f"C{i}" for i in range(1,10)]
    )

    for col in ["A"] + [f"B{i}" for i in range(1,10)] + [f"C{i}" for i in range(1,10)]:
        into = db.collection(name=col)
        print(f"generating documents for {col}")
        docs = [ { "_key": f"doc_{d}",
                   "payload": generate_random_string(100) } for d in range(0, num_docs) ]
        print(f"inserting documents into {col}")
        into.insert(docs)
        print("done")

    e = db.collection(name="E")
    edges = [ { "_from": f"A/doc_{random.randrange(0, num_docs)}",
                "_to": f"B{random.randrange(1,10)}/doc_{random.randrange(0,num_docs)}",
                "payload": generate_random_string(50)}
              for i in range(0,num_edges) ]
    e.insert(edges)

    edges = [ { "_from": f"B1/doc_{random.randrange(0, num_docs)}",
                "_to": f"C{random.randrange(1,10)}/doc_{random.randrange(0,num_docs)}",
                "payload": generate_random_string(50)}
              for i in range(0,num_edges) ]
    f = db.collection(name="F")
    f.insert(edges)
    
def main():
    argparser = argparse.ArgumentParser()
    argparser.add_argument('--num-docs', type=int, default=1000000)
    argparser.add_argument('--num-edges', type=int, default=1000)
    argparser.add_argument('--batch-size', type=int, default=1000)
    args = argparser.parse_args()
    generate(args.num_docs, args.num_edges, args.batch_size)

if __name__ == '__main__':
    main()
