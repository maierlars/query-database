#!/usr/bin/env python3
import json
import click
import listing
from tabulate import tabulate


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
    datasets = listing.get_datasets()

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
    queries = listing.get_test_queries()

    if format == 'plain':
        fields = ["id", "query", "invocation"]
        data = []
        for query in queries:
            for dataset in query["datasets"]:
                data.append([*[query[f] for f in fields], dataset])
        print(tabulate(data, headers=[*fields, "dataset"]))
    elif format == 'jsonl':
        for dataset in queries:
            print(json.dumps(dataset))


if __name__ == "__main__":
    main()
