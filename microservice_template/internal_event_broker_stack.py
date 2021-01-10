import aws_cdk.aws_sns as sns
from aws_cdk import core


class InternalEventBrokerStack(core.Stack):

    def __init__(self, scope: core.Construct, construct_id: str, stage: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self.topic = sns.Topic(
            self,
            f"IEBTopic{stage}",
            display_name=f"Internal Event Broker for {stage}")

        self.topic_output = core.CfnOutput(
            self,
            f"IEBTopic{stage}ArnOutput",
            value=self.topic.topic_arn,
            export_name=f"IEBTopic{stage}Arn")
