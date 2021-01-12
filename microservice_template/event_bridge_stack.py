import aws_cdk.aws_iam as iam
import aws_cdk.aws_sqs as sqs
import aws_cdk.aws_lambda_event_sources as lambda_event_sources
import aws_cdk.aws_lambda as _lambda
import aws_cdk.aws_events as events
import aws_cdk.aws_events_targets as events_targets

from aws_cdk import core


class EventBridgeStack(core.Stack):

    def __init__(self, scope: core.Construct, construct_id: str, stage: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Event bus
        event_bus = events.EventBus(
            self,
            f"EventBus{stage}",
            event_bus_name="SampleEventBus")

        # Producer function
        producer_function = _lambda.Function(
            self,
            'ClientFunction',
            runtime=_lambda.Runtime.PYTHON_3_7,
            code=_lambda.Code.asset('./microservice_template/event_bridge_lambda'),
            handler='producer.handler',
            timeout=core.Duration.seconds(300))

        producer_function.add_environment(
            "EVENT_BUS_ARN",
            event_bus.event_bus_arn)

        producer_function.add_environment(
            "EVENT_BUS_NAME",
            event_bus.event_bus_name)

        event_bus.grant_put_events(producer_function)

        consumer_function = _lambda.Function(
            self,
            'ServerFunction',
            runtime=_lambda.Runtime.PYTHON_3_7,
            code=_lambda.Code.asset('./microservice_template/event_bridge_lambda'),
            handler='consumer.handler',
            timeout=core.Duration.seconds(300))

        event_pattern  = events.EventPattern(account=[self.account])
        target = events_targets.LambdaFunction(handler=consumer_function)
        events.Rule(
            self,
            id="DefaultRule",
            enabled=True,
            rule_name="DefaultRule",
            description="Default rule",
            event_bus=event_bus,
            event_pattern=event_pattern,
            targets=[target])

