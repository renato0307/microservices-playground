import aws_cdk.aws_dynamodb as dyndb
import aws_cdk.aws_lambda as _lambda
import aws_cdk.aws_lambda_event_sources as lambda_event_sources
import aws_cdk.aws_sqs as sqs
from aws_cdk import core


class TransactionalOutbox(core.Construct):

    def __init__(self, scope: core.Construct, id: str, *, prefix=None):
        super().__init__(scope, id)

        message_relay = _lambda.Function(
            self,
            'MessageRelayFunction',
            runtime=_lambda.Runtime.PYTHON_3_7,
            code=_lambda.Code.asset(
                './cloud_playground/transactional_outbox_lambda'),
            handler='message_relay.handler')

        partition_key = dyndb.Attribute(
            name="event_id",
            type=dyndb.AttributeType.STRING)

        self.event_table = dyndb.Table(
            self,
            "EventTable",
            table_name=f"{id}EventTable",
            billing_mode=dyndb.BillingMode.PAY_PER_REQUEST,
            partition_key=partition_key,
            stream=dyndb.StreamViewType.NEW_IMAGE)

        self.event_table.grant_stream_read(message_relay)

        message_relay_dlq = sqs.Queue(
            self,
            "MessageRelayDlq",
            queue_name=f"{id}MessageRelayDlq")

        message_relay.add_event_source(lambda_event_sources.DynamoEventSource(
            self.event_table,
            batch_size=1,
            starting_position=_lambda.StartingPosition.LATEST,
            on_failure=lambda_event_sources.SqsDlq(message_relay_dlq)))
