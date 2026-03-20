import os
import subprocess
import sys

import nanoid
from arango import ArangoClient

from typedefs import Dataset


class SourceProvider:

    def run_restore(self, host: str, database: str, username: str, password: str):
        raise NotImplementedError

class GeneratorCommandSource(SourceProvider):

    def __init__(self, command: list[str], work_dir: str):
        self.command = command
        self.work_dir = work_dir

    def run_restore(self, host: str, database: str, username: str, password: str):
        print(f"Running command {self.command}")
        # copy the current env, so we don't lose PATH or similar
        env = os.environ.copy()
        env.update({
            "ARANGO_HOSTS": host,
            "ARANGO_USERNAME": username,
            "ARANGO_DATABASE": database,
            "ARANGO_PASSWORD": password,
        })

        subprocess.run(args=self.command, env=env, cwd=self.work_dir, check=True, capture_output=False)
        print("subprocess completed")

def construct_source_provider(ds: Dataset):
    description = ds.source_description
    command = description.get("generator_command")
    if command is not None:
        return GeneratorCommandSource(command, os.path.dirname(ds.source_file))

    raise RuntimeError("failed to parse source description")

def _generate_unique_test_database(client: ArangoClient):

    database = f"db_{nanoid.generate()}"
    username = nanoid.generate()
    password = nanoid.generate() # This is not about security

    print(f"Creating database {database}")
    client.db("_system").create_database(database, users=[{"username": username, "password": password}])
    return database, username, password

def _restore_with_provider(host: str, provider: SourceProvider):
    client = ArangoClient(host)
    access = _generate_unique_test_database(client)
    provider.run_restore(host, *access)
    return access


def restore_dataset(ds: Dataset, host: str):
    try:
        provider = construct_source_provider(ds)

        # Todo: how to provide credentials to the script

        return _restore_with_provider(host, provider)

    except RuntimeError as e:
        raise RuntimeError(f"failed to restore dataset {ds.short_name}: {e}") from e


