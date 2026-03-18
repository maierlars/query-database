import functools
import os
from pathlib import Path

import yaml
import fnmatch
from deepmerge import always_merger as deepmerge


def _scan_directory_recursive(directory, fltr=None):
    for dirpath, dirs, filenames in os.walk(directory, topdown=True):
        for filename in filenames:
            if fltr is not None and not fnmatch.fnmatch(filename, fltr):
                continue
            yield os.path.join(dirpath, filename)


def instantiate_query_set(query_set):
    datasets = query_set["datasets"]
    filename = query_set["filename"]

    for query_name, query in query_set["queries"].items():

        # parse query text
        text = query.get("query")
        text_file = query.get("query_file")
        if text_file is not None:
            text = Path(text_file).read_text()

        global_options = query.get("options", {})

        for invocation_name, invocation in query.get("invocations", {}).items():
            bind_param = invocation.get("bind_param")

            local_options = invocation.get("options", {})
            # deep merge of options
            options = deepmerge.merge(global_options, local_options)

            inst = {"datasets": datasets,
                    "query": query_name,
                    "invocation": invocation_name,
                    "id": os.path.join(os.path.dirname(filename), query_name, invocation_name),
                    "query_text": text,
                    "bind_param": bind_param,
                    "filename": filename,
                    "options": options}
            yield inst


@functools.cache
def get_test_queries():
    def generator():
        files = list(_scan_directory_recursive("tests", "*.yaml"))
        wd = os.getcwd()
        for file in files:
            with open(file, "r") as f:
                query_set = yaml.safe_load(f)
                query_set["filename"] = file
                os.chdir(os.path.dirname(file))
                yield from instantiate_query_set(query_set)
                os.chdir(wd)

    return list(generator())

@functools.cache
def get_datasets():
    def generator():
        for file in _scan_directory_recursive("datasets", "*.yaml"):
            with open(file, "r") as f:
                dataset_set = yaml.safe_load(f)
                dataset_set["filename"] = file
                os.chdir(os.path.dirname(file))
                for name, dataset in dataset_set["datasets"].items():
                    dataset["filename"] = file
                    dataset["name"] = name
                    yield dataset

    return list(generator())

if __name__ == "__main__":
    print(get_test_queries())
