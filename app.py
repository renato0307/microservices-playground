
import os

from aws_cdk import core
from contract_testing_stack import ContractTestingStack
from event_bridge_stack import EventBridgeStack
from request_response_messaging_stack import RequestResponseStack

from microservice_template.cloud_service_stack import SampleCloudServiceStack
from microservice_template.internal_event_broker_stack import \
    InternalEventBrokerStack

stage = os.getenv("CDK_STAGE", "Dev")

app = core.App()

ieb_stack = InternalEventBrokerStack(app, f"InternalEventBroker{stage}", stage)
service_stack = SampleCloudServiceStack(app, f"CloudService{stage}", stage)
service_stack.add_dependency(ieb_stack)

request_response_stack = RequestResponseStack(app, f"RequestResponseSample{stage}", stage)

event_bridge_stack = EventBridgeStack(app, f"EventBridge{stage}", stage)

contract_testing_stack = ContractTestingStack(app, f"ContractTesting{stage}", stage)

app.synth()
