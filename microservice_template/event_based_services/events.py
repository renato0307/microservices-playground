import datetime
from enum import Enum
from json import JSONEncoder
from typing import List

import pydantic


class OperationTypeEnum(str, Enum):
    create_tenant = 'create_tenant'
    assign_tenant = 'assign_tenant'
    delete_tenant = 'delete_tenant'


class DetailTypeEnum(str, Enum):
    # Create tenant events
    create_tenant = 'create_tenant'
    create_tenant_done = 'create_tenant_done'

    create_tenant_infrastructure = 'create_tenant_infrastructure'
    create_tenant_infrastructure_done = 'create_tenant_infrastructure_done'

    preprovisiong_license = 'preprovisiong_license'
    preprovisiong_license_done = 'preprovisiong_license_done'

    # Assign tenant events
    assign_tenant = 'assign_tenant'

    assign_tenant_infrastructure = 'assign_tenant_infrastructure'
    assign_tenant_infrastructure_done = 'assign_tenant_infrastructure_done'

    create_user = 'create_user'
    create_user_done = 'create_user_done'

    update_license = 'update_license'
    update_license_done = 'update_license_done'

    # Delete tenant events
    delete_tenant = 'delete_tenant'
    delete_tenant_infrastructure_done = 'delete_tenant_infrastructure_done'
    delete_license_done = 'delete_tenant_license_done'


class BaseEvent(pydantic.BaseModel):
    # header
    uuid: str
    correlation_id: str
    source: str
    detail_type: str
    timestamp: datetime.datetime

    operation_uuid: str
    operation_type: str

    termination_table: List[str]


class TenantEvent(BaseEvent):
    # body
    tenant_id: str


class EventEncoder(JSONEncoder):
    # Override the default method
    def default(self, obj):
        if isinstance(obj, (datetime.date, datetime.datetime)):
            return obj.isoformat()
