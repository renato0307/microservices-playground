from diagrams import Cluster, Diagram, Edge
from diagrams.aws.compute import Lambda
from diagrams.aws.database import DynamodbTable
from diagrams.aws.integration import SQS, SimpleNotificationServiceSns

with Diagram("Cloud Service", show=False):

    with Cluster("Task"):
        lambda_handler = Lambda("Handler")
        task_table = DynamodbTable("Task Table")

    with Cluster("TransactionalOutbox"):
        outbox_table = DynamodbTable("Outbox Table")
        message_relay_handler = Lambda("MessageRelay Handler")
        message_relay_dlq = SQS("MessageRelayDlq")

    with Cluster("Internal Event Broker"):
        ieb = SimpleNotificationServiceSns("Topic")

    lambda_handler >> task_table

    lambda_handler >> outbox_table

    outbox_table >> Edge(label="table stream") >> message_relay_handler
    message_relay_handler >> Edge(label="on failure") >> message_relay_dlq

    message_relay_handler >> Edge(label="on success") >> ieb
