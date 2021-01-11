import aws_cdk.aws_iam as iam
import aws_cdk.aws_sqs as sqs
import aws_cdk.aws_lambda_event_sources as lambda_event_sources
import aws_cdk.aws_lambda as _lambda

from aws_cdk import core


class RequestResponseStack(core.Stack):

    def __init__(self, scope: core.Construct, construct_id: str, stage: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        request_queue = sqs.Queue(self, f"RRRequestQueue{stage}", visibility_timeout=core.Duration.seconds(300))

        # Client function
        client_function = _lambda.Function(
            self,
            'ClientFunction',
            runtime=_lambda.Runtime.PYTHON_3_7,
            code=_lambda.Code.asset('./microservice_template/request_response_messaging'),
            handler='client.handler',
            timeout=core.Duration.seconds(300))

        client_function.add_environment(
            "REQUEST_QUEUE",
            request_queue.queue_url)

        client_function.add_to_role_policy(
            iam.PolicyStatement(
                resources=["*"],
                effect=iam.Effect.ALLOW,
                actions=["sqs:CreateQueue", "sqs:TagQueue"]))

        request_queue.grant_send_messages(client_function)

        # Server function
        server_function = _lambda.Function(
            self,
            'ServerFunction',
            runtime=_lambda.Runtime.PYTHON_3_7,
            code=_lambda.Code.asset('./microservice_template/request_response_messaging'),
            handler='server.handler',
            timeout=core.Duration.seconds(300))

        server_function.add_event_source(lambda_event_sources.SqsEventSource(
            request_queue,
            batch_size=1,))
        
        request_queue.grant_consume_messages(server_function)