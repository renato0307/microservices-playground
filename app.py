
import os

from aws_cdk import core

from microservice_template.cloud_service_stack import SampleCloudServiceStack
from microservice_template.internal_event_broker_stack import \
    InternalEventBrokerStack

stage = os.getenv("CDK_STAGE", "Dev")

app = core.App()

ieb_stack = InternalEventBrokerStack(app, f"InternalEventBroker{stage}", stage)

service_stack = SampleCloudServiceStack(app, f"CloudService{stage}", stage)

service_stack.add_dependency(ieb_stack)

app.synth()
