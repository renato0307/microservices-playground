
import moto
from microservice_template.event_based_services.event_ledger import (
    EventModel, handler)


@moto.mock_dynamodb2
def test_event_ledger():

    EventModel.create_table(read_capacity_units=1, write_capacity_units=1)

    event = {
        'version': '0',
        'id': '8a828b2c-116b-84ec-7ebd-42ebaabdd381',
        'detail-type': 'delete_tenant',
        'source': 'OperationsProxy',
        'account': '920101814014',
        'time': '2021-01-17T00:18:19Z',
        'region': 'eu-west-1',
        'resources': [],
        'detail': {
            'uuid': '35fcddc3-b616-4acf-a6dc-40977b036cfe',
            'correlation_id': '35fcddc3-b616-4acf-a6dc-40977b036cfe',
            'source': 'OperationsProxy',
            'detail_type': 'delete_tenant',
            'timestamp': '2021-01-17T00:18:18.936194+00:00',
            'operation_uuid': 'ba686497-3de3-438d-9c28-ade93e28b5cb',
            'operation_type': 'delete_tenant',
            'termination_table': ['delete_tenant_infrastructure_done', 'delete_tenant_license_done'],
            'tenant_id': '5'
        }
    }
    context = {}
    handler(event, context)
