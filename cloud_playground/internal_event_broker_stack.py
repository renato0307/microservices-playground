import aws_cdk.aws_sns as sns
from aws_cdk import core


class InternalEventBrokerStack(core.Stack):

    def __init__(self, scope: core.Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        topic = sns.Topic(self, "IEBTopic",
                          display_name="Internal Event Broker")

        core.CfnOutput(self, "IEBTopicArnOutput",
                       value=topic.topic_arn, export_name="IEBTopicArn")
