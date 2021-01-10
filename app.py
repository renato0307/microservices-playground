
import os

from aws_cdk import core

from cloud_playground.cloud_service_stack import CloudServiceStack
from cloud_playground.internal_event_broker_stack import \
    InternalEventBrokerStack

stage = os.getenv("CDK_STAGE", "Dev")

app = core.App()
CloudServiceStack(app, f"CloudService{stage}")
InternalEventBrokerStack(app, f"InternalEventBroker{stage}")

app.synth()
