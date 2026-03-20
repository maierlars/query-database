from pydantic.dataclasses import dataclass

@dataclass
class Dataset:
    source_file: str
    short_name: str
    id: str
    source_description: dict


@dataclass
class QueryInvocation:
    query_text: str
    bind_parameter: dict
    datasets: list[str]
    source_file: str
    invocation_name: str
    query_name: str
    id: str
    options: dict
