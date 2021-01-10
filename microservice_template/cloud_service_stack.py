import aws_cdk.aws_dynamodb as dyndb
import aws_cdk.aws_lambda as _lambda
import aws_cdk.aws_lambda_python as _lambda_py
from aws_cdk import core

from cloud_playground.transactional_outbox_construct import TransactionalOutbox


class CloudServiceStack(core.Stack):
    def __init__(self, scope: core.Construct, construct_id: str, stage: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self.stage = stage

        self._setup_stack(scope, construct_id, stage)

    def _setup_stack(self, scope: core.Construct, construct_id: str, stage: str):
        func = self.setup_stack(scope, construct_id, stage)

        outbox = TransactionalOutbox(
            self,
            "CloudServiceTransactionalOutbox",
            stage)
        outbox.event_table.grant_full_access(func)

        func.add_environment(
            "OUTBOX_TABLE_NAME",
            outbox.event_table.table_name)

    def setup_stack(self, scope: core.Construct, construct_id: str, stage: str) -> _lambda.Function:
        raise Exception("Not implemented")


class SampleCloudServiceStack(CloudServiceStack):

    def __init__(self, scope: core.Construct, construct_id: str, stage: str, **kwargs) -> None:
        super().__init__(scope, construct_id, stage, **kwargs)

    def setup_stack(self, scope: core.Construct, construct_id: str, stage: str) -> _lambda.Function:
        layer = _lambda_py.PythonLayerVersion(
            self,
            'TaskLayer',
            entry='./cloud_playground/task_lambda_layer')

        task_function = _lambda.Function(
            self,
            'TaskFunction',
            runtime=_lambda.Runtime.PYTHON_3_7,
            code=_lambda.Code.asset('./cloud_playground/task_lambda'),
            layers=[layer],
            handler='do_task.handler',
            timeout=core.Duration.seconds(300))

        partition_key = dyndb.Attribute(
            name="task_id",
            type=dyndb.AttributeType.STRING)

        task_table = dyndb.Table(
            self,
            "DummyTaskTable",
            table_name=f"{construct_id}DummyTaskTable",
            billing_mode=dyndb.BillingMode.PAY_PER_REQUEST,
            partition_key=partition_key)

        task_table.grant_full_access(task_function)

        task_function.add_environment(
            "TASK_TABLE_NAME",
            task_table.table_name)

        return task_function
