import os
os.environ["PRODUCER_ENDPOINT"] = "http://localhost:1234/prod"

import atexit
from microservice_template.contract_testing_services.consumer import handler

from pact import Consumer, Provider


pact = Consumer('Consumer').has_pact_with(Provider('Provider'), pact_dir="pacts")
pact.start_service()
atexit.register(pact.stop_service)


def test_get_value():

    expected = {
        "message": "Go Serverless v1.0! Your function executed successfully!",
        "field1": "Some value for this testing field",
        "input": "XXX"
    }

    (pact
     .given('The existence of a producer')
     .upon_receiving('a request from the consumer')
     .with_request('get', '/prod')
     .will_respond_with(200, body=expected))

    with pact:
      result = handler({}, {})

    assert result["body"] == expected["field1"]