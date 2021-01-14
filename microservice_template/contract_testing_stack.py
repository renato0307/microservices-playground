import aws_cdk.aws_dynamodb as dyndb
import aws_cdk.aws_lambda as _lambda
import aws_cdk.aws_apigateway as apigw
import aws_cdk.aws_lambda_python as _lambda_py
from aws_cdk import core


class ContractTestingStack(core.Stack):

    def __init__(self, scope: core.Construct, construct_id: str, stage: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        layer = _lambda_py.PythonLayerVersion(
            self,
            'LambdaLayer',
            entry='./microservice_template/contract_testing_services_layer')

        producer_function = _lambda.Function(
            self,
            'ProducerFunction',
            runtime=_lambda.Runtime.PYTHON_3_7,
            code=_lambda.Code.asset('./microservice_template/contract_testing_services'),
            layers=[layer],
            handler='producer.handler',
            timeout=core.Duration.seconds(300))

        producer_api = apigw.LambdaRestApi(
            self, 'ProducerEndpoint',
            handler=producer_function,
        )

        consumer_function = _lambda.Function(
            self,
            'ConsumerFunction',
            runtime=_lambda.Runtime.PYTHON_3_7,
            code=_lambda.Code.asset('./microservice_template/contract_testing_services'),
            layers=[layer],
            handler='consumer.handler',
            timeout=core.Duration.seconds(300))

        apigw.LambdaRestApi(
            self, 'ConsumerEndpoint',
            handler=consumer_function,
        )

        consumer_function.add_environment(
            "PRODUCER_ENDPOINT",
            producer_api.url)