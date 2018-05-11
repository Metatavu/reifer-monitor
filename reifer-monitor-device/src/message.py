from typing import NamedTuple
from typing import Any
from traceback import StackSummary

class BatchNameQueryRequest(NamedTuple):
    batch_code: str

class BatchNameQueryResponse(NamedTuple):
    batch_name: str

class BatchAssociationRequest(NamedTuple):
    batch_name: str
    batch_code: str

class BatchAssociationResponse(NamedTuple):
    batch_id: int

class ErrorResponse(NamedTuple):
    exception: Exception
    stack_summary: StackSummary