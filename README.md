
# ArangoDB Query Database

A huge collection of ideally real-world queries that are tested for performance and correctness.

## Introduction

### Why do we need this?
- The state of performance tests at ArangoDB is insufficient. There are many incompatible and hard-to-maintain test frameworks that test very specific aspects. They do not reflect real-world use-cases.
- Optimizer tests check only very specific and small queries, which are tailored to invoke the optimizer rule under test. There are very few cross-functionality tests and tests on real world queries and datasets. Thus, changes to the optimizer can barely be evaluated for correctness. 
- Correctness of results is rarely scrutinized in performance tests yielding misleading "optimized" outcomes.

### Goals

- **Easy to add new performance tests:** It should be very easy to add new performance tests, even for Solution Architects or Support Engineers. Given a dataset, for example, extracted using arangodump, and a set of queries, essentially no programming must be necessary to add those as performance test.
- **Cover performance and correctness:** The Query Database consists of datasets, queries and expected result sets. A performance run is meaningless if it does not produce the correct result.
- **Cover all aspects of query execution:** The total runtime of a query does not only consist of the execution time, but the runtime of the optimizer can affect the overall performance significantly, in particular on short-running queries.
- **Alerts on performance phenomenons:** While this certainly contains degradation and changes in the z-Score, a higher variance is also something we want to look out for. This should be an automatic test that does not require a human to look at the dashboard. This includes tracking errors during execution.
- **Regular execution and explicit PR execution:** The test set should run at least twice a week. It must be possible to run the tests for a specific branch and get a report about possible regressions.
- **Clear visibility of results:** Use a state-of-the-art Grafana dashboard to show the performance tests. Explicit PR reports should be easy to digest and clearly show relevant information on changes in performance.
- **Restrict to cluster execution:** Cluster is the primary use case. Let's focus on that first. We restrict ourselves to a setup that consists of three (3) database servers.
- **Focus on Reading and AQL:** The first version shall focus on read-only queries and use AQL.
- **Queries and Datasets are immutable:** Once a dataset or a query has been added to the query database, they shall not be changed. Many queries depend on different datasets and changing those just causes confusion and might break things unnecessarily.
- **Usable for SLAs**: Eventually this framework shall be used to evaluate the performance of ArangoDB with respect to SLAs and customer requirements.

## Usage
```bash
# List resources
src/main.py list queries
src/main.py list datasets

# Restore a specific dataset
src/main.py restore <dataset> [--endpoint <endpoint>]
```

## Development

### Create a virtual environment
```bash
python3 -m venv venv
source venv/bin/activate
```

### Install requirements
```bash
pip install -r requirements.txt
```

### Adding new requirements
Use the virtual environment to add new dependencies. Then update the `requirements.txt` like so:
```
pip freeze > requirements.txt
```