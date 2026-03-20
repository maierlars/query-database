import functools
import os
from pathlib import Path

import yaml
from deepmerge import always_merger as deepmerge
from typedefs import Dataset, QueryInvocation
from contextlib import chdir

def instantiate_query_set(filename : Path):
    definition = yaml.safe_load(filename.read_text())
    datasets = definition["datasets"]

    with chdir(filename.parent):
        for query_name, query in definition["queries"].items():

            # parse query text
            text = query.get("query")
            text_file = query.get("query_file")
            if text_file is not None:
                text = Path(text_file).read_text()

            global_options = query.get("options", {})

            for invocation_name, invocation in query.get("invocations", {}).items():
                bind_param = invocation.get("bind_param", {})

                local_options = invocation.get("options", {})
                # deep merge of options
                options = deepmerge.merge(global_options, local_options)

                id_str = str(os.path.join(os.path.dirname(filename), query_name, invocation_name))
                yield QueryInvocation(
                    query_name=query_name,
                    invocation_name=invocation_name,
                    id=id_str,
                    query_text=text,
                    bind_parameter=bind_param,
                    source_file=str(filename),
                    options=options,
                    datasets=datasets)

@functools.cache
def get_test_queries() -> dict[str, QueryInvocation]:

    all_queries = {}
    for file_path in Path("tests").rglob("*.yaml"):
        try:
            queries = instantiate_query_set(file_path)
        except RuntimeError as e:
            raise RuntimeError(f"failed to parse query set file `{file_path}`: {e}") from e

        for q in queries:
            all_queries[q.id] = q

    return all_queries

def _read_dataset_file(filename: Path):
    with open(filename, "r") as f:
        dataset_file = yaml.safe_load(f)
        for name, dataset in dataset_file["datasets"].items():
            id_str = str(os.path.join(os.path.dirname(filename), name))
            yield Dataset(
                source_file=str(filename),
                short_name=name,
                id=id_str,
                source_description=dataset["source"]
            )


@functools.cache
def get_datasets() -> dict[str, Dataset]:
    all_datasets = {}

    # rglob("*.yaml") handles the recursive search natively
    for file_path in Path("datasets").rglob("*.yaml"):
        try:
            # .extend() adds the list returned by _read_dataset_file to our main list
            datasets = _read_dataset_file(file_path)
        except RuntimeError as e:
            raise RuntimeError(f"failed to parse dataset file `{file_path}`: {e}") from e

        for ds in datasets:
            all_datasets[ds.id] = ds

    return all_datasets