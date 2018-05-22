from traceback import StackSummary
from typing import Any, NamedTuple, Optional


class BatchNameQueryRequest(NamedTuple):
    batch_code: str

class BatchNameQueryResponse(NamedTuple):
    batch_name: Optional[str]

class BatchAssociationRequest(NamedTuple):
    batch_code: str
    batch_name: str

class BatchAssociationResponse(NamedTuple):
    batch_id: int

class StartActivityPeriodRequest(NamedTuple):
    workstation_code: str
    num_workers: int

class StartActivityPeriodResponse(NamedTuple):
    pass

class StopActivityPeriodRequest(NamedTuple):
    workstation_code: str

class StopActivityPeriodResponse(NamedTuple):
    pass

class StartWorkRunRequest(NamedTuple):
    workstation_code: str

class StartWorkRunResponse(NamedTuple):
    pass

class StopWorkRunRequest(NamedTuple):
    workstation_code: str

class StopWorkRunResponse(NamedTuple):
    pass

class StartWorkRequest(NamedTuple):
    workstation_code: str
    batch_code: str

class StartWorkResponse(NamedTuple):
    pass

class StopWorkRequest(NamedTuple):
    workstation_code: str

class StopWorkResponse(NamedTuple):
    pass

class ErrorResponse(NamedTuple):
    exception: Exception
    stack_summary: StackSummary
