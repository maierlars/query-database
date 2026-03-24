#!/usr/bin/env python3
import arango
import os
import argparse
import random
import string
import multiprocessing

ARANGO_HOSTS = os.environ['ARANGO_HOSTS']
ARANGO_USERNAME = os.environ['ARANGO_USERNAME']
ARANGO_PASSWORD = os.environ['ARANGO_PASSWORD']
ARANGO_DATABASE = os.environ['ARANGO_DATABASE']

def generate_random_string(length):
    return ''.join(random.choice(string.ascii_uppercase) for i in range(length))

def generate_vertex_collection(args):
    db = args[0]
    num_docs = args[1]
    collection = args[2]

    print(f"Inserting docs into {collection}")

    into = db.collection(name=collection)
    docs = [ { "_key": f"doc_{d}",
               "payload": generate_random_string(100) } for d in range(0, num_docs) ]
    into.insert(docs)

def generate_E_edges(db, num_docs, num_edges):
    e = db.collection(name="E")
    print("generating edges for E")
    edges = [ { "_key": f"{i}",
                "_from": f"A/doc_{random.randrange(0, num_docs)}",
                "_to": f"B{random.randrange(1,10)}/doc_{random.randrange(0,num_docs)}",
                "payload": generate_random_string(50)}
              for i in range(0,num_edges) ]
    print(f"inserting edges into E")
    e.insert(edges)
    print("done inserting into E")

def generate_F_edges(db, num_docs, num_edges):
    f = db.collection(name="F")
    print("generating edges for F")
    edges = [ { "_key": f"{i}",
                "_from": f"B1/doc_{random.randrange(0, num_docs)}",
                "_to": f"C{random.randrange(1,10)}/doc_{random.randrange(0,num_docs)}",
                "payload": generate_random_string(50)}
              for i in range(0,num_edges) ]
    print(f"inserting edges into F")
    f.insert(edges)
    print("done inserting into F")
 
def generate(num_docs, num_edges, batch_size):
    client = arango.ArangoClient(hosts=ARANGO_HOSTS)

    db = client.db(ARANGO_DATABASE, username=ARANGO_USERNAME, password=ARANGO_PASSWORD)
    hopgraph = db.create_graph("hopgraph")

    # The idea of this graph benchmark is that there are vertex collections
    # A, B_1, B_2, ..., B_9, C_1, C2, ..., C_9 and edge collections E and F
    # with edges going from A to B_i and from B_1 (!) to C_i 
    #
    # The queries executed in the attached benchmark try to find paths from a
    # vertex in A to a vertex in C_1 (!)
    #
    # (likely intended to prove the superiority of iterated joins over traversals)

    E = hopgraph.create_edge_definition(
        edge_collection="E",
        from_vertex_collections=["A"],
        to_vertex_collections=[f"B{i}" for i in range(1,10)]
    )
    F = hopgraph.create_edge_definition(
        edge_collection="F",
        # It is intentional that the graph defintion only covers
        # B1 -> C{i}
        from_vertex_collections=["B1"],
        to_vertex_collections=[f"C{i}" for i in range(1,10)]
    )

    collections = ["A"] + [f"B{i}" for i in range(1,10)] + [f"C{i}" for i in range(1,10)]
    args = [(db, num_docs, coll) for coll in collections]
    pool = multiprocessing.Pool(processes=multiprocessing.cpu_count())
    pool.apply_async(generate_E_edges, [db, num_docs, num_edges])
    pool.map_async(generate_vertex_collection, args)
    pool.apply_async(generate_F_edges, [db, num_docs, num_edges])
    
    pool.close()
    pool.join()

   
def main():
    argparser = argparse.ArgumentParser()
    argparser.add_argument('--num-docs', type=int, default=1000000)
    argparser.add_argument('--num-edges', type=int, default=1000)
    argparser.add_argument('--batch-size', type=int, default=1000)
    argparser.add_argument('--seed', type=int, default=0)
    args = argparser.parse_args()
    generate(args.num_docs, args.num_edges, args.batch_size)

if __name__ == '__main__':
    main()
