from arango import ArangoClient

from typedefs import QueryInvocation, DatabaseAccess

class ProfileResultsReporter:

    def report(self, query: QueryInvocation, num_run: int, result):
        raise NotImplementedError


class PrintReporter(ProfileResultsReporter):
    def report(self, query: QueryInvocation, num_run: int, result):
        print(query.id, num_run, result)


def profile_query(query: QueryInvocation, access: DatabaseAccess, reporter: ProfileResultsReporter):
    client = ArangoClient(hosts=access.hostname)
    db = client.db(access.database, access.username, access.password)

    print(f"Performing {query.warm_up_runs} warm up runs...")
    for idx in range(query.warm_up_runs):
        # TODO check for errors here?
        db.aql.execute(query=query.query_text, bind_vars=query.bind_parameter, profile=True)

    print(f"Performing {query.number_of_runs} test runs...")
    for idx in range(query.number_of_runs):
        result = db.aql.execute(query=query.query_text, bind_vars=query.bind_parameter, profile=True)

        reporter.report(query, idx, result.profile())
