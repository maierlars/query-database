#!/usr/bin/env python3
import dataclasses
import json
import click
import listing
from tabulate import tabulate

from restore_dataset import restore_dataset
import check_query


@click.group()
def main():
    pass


@main.group()
def list():
    """List resources of a specific type"""
    pass


@list.command()
@click.option('--format',
              type=click.Choice(['jsonl', 'plain'], case_sensitive=False),
              default='plain',
              help="Output format for the listing.")
def datasets(format):
    """List datasets"""
    datasets = listing.get_datasets().values()

    if format == 'plain':
        print(tabulate(datasets, headers="keys"))
    elif format == 'jsonl':
        for dataset in datasets:
            print(json.dumps(dataset))


@list.command()
@click.option('--format',
              type=click.Choice(['jsonl', 'plain'], case_sensitive=False),
              default='plain',
              help="Output format for the listing.")
def queries(format):
    """List queries"""
    all_queries = listing.get_test_queries().values()

    if format == 'plain':
        fields = ["id", "query_name", "invocation_name", "datasets"]
        data = []
        for query in all_queries:
            data.append([getattr(query, f) for f in fields])
        print(tabulate(data, headers=fields))
    elif format == 'jsonl':
        for query in all_queries:
            print(json.dumps(dataclasses.asdict(query)))

@main.command()
@click.argument("dataset")
@click.option('--endpoint',
              type=str,
              default='http://localhost:8530/',
              help="ArangoDB instance to be used")
def restore(dataset: str, endpoint: str):
    """Restores the given dataset into a database"""
    all_datasets = listing.get_datasets()
    access = restore_dataset(all_datasets[dataset], endpoint)
    print(f"database: {access[0]}")
    print(f"username: {access[1]}")
    print(f"password: {access[2]}")


@main.command()
@click.argument("query-id")
@click.argument("database")
@click.argument("username")
@click.argument("password")
@click.option('--endpoint',
              type=str,
              default='http://localhost:8530/',
              help="ArangoDB instance to be used")
def create_result(query_id: str, database: str, username: str, password: str, endpoint: str):
    """Creates a result file for the given query"""
    all_queries = listing.get_test_queries()
    query = all_queries[query_id]

    filename = check_query.create_query_result(query, {
        "host": endpoint,
        "database": database,
        "username": username,
        "password": password
    })

    print(f"Query result written to `{filename}`")

@main.command()
@click.argument("query-id")
@click.argument("database")
@click.argument("username")
@click.argument("password")
@click.option('--endpoint',
              type=str,
              default='http://localhost:8530/',
              help="ArangoDB instance to be used")
def profile(query_id: str, database: str, username: str, password: str, endpoint: str):
    """Runs a single profiler run for the given query"""
    all_queries = listing.get_test_queries()
    query = all_queries[query_id]

    results = check_query.profile_query(query, {
        "host": endpoint,
        "database": database,
        "username": username,
        "password": password
    })

    data = [
        (name, f"{1000*delta:.3f}ms") for name, delta in results.items()
    ]

    print(tabulate(data, headers=["Stage", "Time"]))


if __name__ == "__main__":
    main()
