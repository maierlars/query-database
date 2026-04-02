import os
import subprocess

import nanoid
from arango import ArangoClient

from typedefs import Dataset, DatabaseAccess, ConnectionAccess


class SourceProvider:

    def run_restore(self, access: DatabaseAccess):
        raise NotImplementedError

class GeneratorCommandSource(SourceProvider):

    def __init__(self, command: list[str], work_dir: str):
        self.command = command
        self.work_dir = work_dir

    def run_restore(self, access: DatabaseAccess):
        print(f"Running command {self.command}")
        # copy the current env, so we don't lose PATH or similar
        env = os.environ.copy()
        env.update({
            "ARANGO_HOSTS": access.hostname,
            "ARANGO_USERNAME": access.username,
            "ARANGO_DATABASE": access.database,
            "ARANGO_PASSWORD": access.password,
        })

        subprocess.run(args=self.command, env=env, cwd=self.work_dir, check=True, capture_output=False)
        print("subprocess completed")

def construct_source_provider(ds: Dataset):
    description = ds.source_description
    command = description.get("generator_command")
    if command is not None:
        return GeneratorCommandSource(command, os.path.dirname(ds.source_file))

    raise RuntimeError("failed to parse source description")

def _generate_unique_test_database(access: ConnectionAccess) -> DatabaseAccess:

    client = ArangoClient(access.hostname)
    database = f"db_{nanoid.generate()}"
    username = nanoid.generate()
    password = nanoid.generate() # This is not about security but to prevent generator script malfunction.

    print(f"Creating database {database}")
    client.db("_system", username, password).create_database(database, users=[{"username": username, "password": password}])
    return DatabaseAccess(access.hostname, username, password, database)

def _restore_with_provider(access: ConnectionAccess, provider: SourceProvider):
    derived_access = _generate_unique_test_database(access)
    provider.run_restore(derived_access)
    return derived_access


def restore_dataset(ds: Dataset, access: ConnectionAccess):
    try:
        provider = construct_source_provider(ds)
        return _restore_with_provider(access, provider)

    except RuntimeError as e:
        raise RuntimeError(f"failed to restore dataset {ds.short_name}: {e}") from e


def remove_dataset(access: ConnectionAccess, database: str):
    client = ArangoClient(access.hostname)
    db = client.db("_system", access.username, access.password)

    print(f"Removing dataset - dropping database {database}")
    db.delete_database(database)
    print("Running compaction")
    db.compact()