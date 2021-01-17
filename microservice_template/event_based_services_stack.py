import aws_cdk.aws_apigateway as apigw
import aws_cdk.aws_dynamodb as dyndb
import aws_cdk.aws_events as events
import aws_cdk.aws_events_targets as events_targets
import aws_cdk.aws_iam as iam
import aws_cdk.aws_lambda as _lambda
import aws_cdk.aws_lambda_event_sources as lambda_event_sources
import aws_cdk.aws_lambda_python as _lambda_py
import aws_cdk.aws_sqs as sqs
from aws_cdk import core


class EventBasedServicesStack(core.Stack):

    def __init__(self, scope: core.Construct, construct_id: str, stage: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self.create_bus(stage)
        self.create_lambda_layer(stage)

        self.create_operations_proxy(stage)
        self.create_event_ledger(stage)
        self.create_saga_termination_checker(stage)

        self.create_history_service(stage)

        self.create_delete_tenant_infra_operation(stage)
        self.create_delete_tenant_license_operation(stage)

    def create_bus(self, stage):
        """Creates Event bus"""

        self.event_bus = events.EventBus(
            self,
            f"InternalEventBus{stage}",
            event_bus_name=f"InternalEventBus{stage}")

    def create_lambda_layer(self, stage):
        """ Creatas the Layer for the lambdas"""

        self.layer = _lambda_py.PythonLayerVersion(
            self,
            f'LambdaLayer{stage}',
            entry='./microservice_template/event_based_services_layer')

    def create_operations_proxy(self, stage):
        """Creates the Operations Proxy API"""

        ops_proxy_function = _lambda.Function(
            self,
            f"OperationsProxyFunction{stage}",
            runtime=_lambda.Runtime.PYTHON_3_7,
            code=_lambda.Code.asset(
                './microservice_template/event_based_services'),
            layers=[self.layer],
            handler='operations_proxy.handler',
            timeout=core.Duration.seconds(300))

        ops_proxy_function.add_environment(
            "EVENT_BUS_NAME",
            self.event_bus.event_bus_name)

        self.event_bus.grant_put_events(ops_proxy_function)

        apigw.LambdaRestApi(
            self,
            f"OperationsProxyApi{stage}",
            handler=ops_proxy_function)

    def create_history_service(self, stage):
        """Creates the history service"""

        history_function = _lambda.Function(
            self,
            f"HistoryFunction{stage}",
            runtime=_lambda.Runtime.PYTHON_3_7,
            code=_lambda.Code.asset(
                './microservice_template/event_based_services'),
            layers=[self.layer],
            handler='history.handler',
            timeout=core.Duration.seconds(300))

        event_pattern = events.EventPattern(account=[self.account])
        target = events_targets.LambdaFunction(handler=history_function)
        events.Rule(
            self,
            id='HistorySubscription',
            enabled=True,
            rule_name="HistorySubscription",
            description="History subscribes to all events in the bus",
            event_bus=self.event_bus,
            event_pattern=event_pattern,
            targets=[target])

    def create_delete_tenant_infra_operation(self, stage):
        """Creates the delete tenant infrastructure operation"""

        delete_tenant_infra_function = _lambda.Function(
            self,
            f"DeleteTenantInfrastructureOperationFunction{stage}",
            runtime=_lambda.Runtime.PYTHON_3_7,
            code=_lambda.Code.asset(
                './microservice_template/event_based_services'),
            layers=[self.layer],
            handler='delete_tenant_infrastructure_operation.handler',
            timeout=core.Duration.seconds(300))

        event_pattern = events.EventPattern(
            account=[self.account],
            detail_type=["delete_tenant"])
        target = events_targets.LambdaFunction(
            handler=delete_tenant_infra_function)
        events.Rule(
            self,
            id='DeliverDeleteTenantEventToDeleteTenantInfrastructureOperation',
            enabled=True,
            rule_name='DeliverDeleteTenantEventToDeleteTenantInfrastructureOperation',
            description='Delete tenant infrastructure operation',
            event_bus=self.event_bus,
            event_pattern=event_pattern,
            targets=[target])

        delete_tenant_infra_function.add_environment(
            "EVENT_BUS_NAME",
            self.event_bus.event_bus_name)

        self.event_bus.grant_put_events(delete_tenant_infra_function)

    def create_delete_tenant_license_operation(self, stage):
        """Creates the delete tenant license operation"""

        delete_tenant_infra_function = _lambda.Function(
            self,
            f"DeleteTenantLicenseOperationFunction{stage}",
            runtime=_lambda.Runtime.PYTHON_3_7,
            code=_lambda.Code.asset(
                './microservice_template/event_based_services'),
            layers=[self.layer],
            handler='delete_license_operation.handler',
            timeout=core.Duration.seconds(300))

        event_pattern = events.EventPattern(
            account=[self.account],
            detail_type=["delete_tenant"])
        target = events_targets.LambdaFunction(
            handler=delete_tenant_infra_function)
        events.Rule(
            self,
            id='DeliverDeleteTenantEventToDeleteTenantLicenseOperation',
            enabled=True,
            rule_name='DeliverDeleteTenantEventToDeleteTenantLicenseOperation',
            description='Delete tenant license operation',
            event_bus=self.event_bus,
            event_pattern=event_pattern,
            targets=[target])

        delete_tenant_infra_function.add_environment(
            "EVENT_BUS_NAME",
            self.event_bus.event_bus_name)

        self.event_bus.grant_put_events(delete_tenant_infra_function)

    def create_event_ledger(self, stage):
        """Creates mechanism to register all events"""

        event_ledger_function = _lambda.Function(
            self,
            f"EventLedgerFunction{stage}",
            runtime=_lambda.Runtime.PYTHON_3_7,
            code=_lambda.Code.asset(
                './microservice_template/event_based_services'),
            layers=[self.layer],
            handler='event_ledger.handler',
            timeout=core.Duration.seconds(300))

        event_pattern = events.EventPattern(account=[self.account])
        target = events_targets.LambdaFunction(
            handler=event_ledger_function)
        events.Rule(
            self,
            id='DeliverAllEventsToEventLedger',
            enabled=True,
            rule_name='DeliverAllEventsToEventLedger',
            description='Deliver all events to event ledger',
            event_bus=self.event_bus,
            event_pattern=event_pattern,
            targets=[target])

        events_ledger = dyndb.Table(
            self,
            f"EventsLedger{stage}",
            table_name=f"EventsLedger{stage}",
            billing_mode=dyndb.BillingMode.PAY_PER_REQUEST,
            partition_key=dyndb.Attribute(
                name="event_uuid",
                type=dyndb.AttributeType.STRING),
            sort_key=dyndb.Attribute(
                name="detail_type",
                type=dyndb.AttributeType.STRING))

        events_ledger.grant_full_access(event_ledger_function)

        event_ledger_function.add_environment(
            "TABLE_NAME",
            events_ledger.table_name)

        event_ledger_function.add_environment(
            "TABLE_REGION",
            self.region)

    def create_saga_termination_checker(self, stage):
        """Creates mechanism to register all events"""

        pass
