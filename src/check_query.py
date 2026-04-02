import arango.database
import json

import sys
from arango import ArangoClient

from typedefs import QueryInvocation
import tempfile


def write_query_result_to_temp_file(query: QueryInvocation, client: arango.database.Database, outfile):
    # TODO add options
    result = client.aql.execute(query=query.query_text, bind_vars=query.bind_parameter)
    for row in result:
        json.dump(row, outfile)
        outfile.write("\n")
    return outfile

def create_query_result(query: QueryInvocation, access):
    filename = tempfile.NamedTemporaryFile(mode="w", delete=False)
    client = ArangoClient(hosts=access["host"])
    db = client.db(access["database"], username=access["username"], password=access["password"])

    write_query_result_to_temp_file(query, db, filename)

    return filename.name
