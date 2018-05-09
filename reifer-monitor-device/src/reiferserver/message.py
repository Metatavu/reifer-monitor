from typing import NamedTuple

class BatchNameQueryRequest(NamedTuple):
    batch_code: str

class BatchNameQueryResponse(NamedTuple):
    batch_name: str

class ErrorResponse(NamedTuple):
    error_type: str
    error_message: str