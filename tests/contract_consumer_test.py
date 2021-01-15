import atexit
import os

from microservice_template.contract_testing_services.consumer import \
    create_random_users
from pact import Consumer, Provider
from pact.matchers import Like

os.environ["PRODUCER_ENDPOINT"] = "http://localhost:1234/"


pact = Consumer('Consumer').has_pact_with(
    Provider('Provider'),
    pact_dir="pacts")
pact.start_service()
atexit.register(pact.stop_service)


def test_get_value():

    expected = {
        "user_name": Like("fake_user_name"),
        "email": Like("fake_email"),
        "name": Like("fake_name"),
    }

    (pact
     .given('The existence of a producer')
     .upon_receiving('a request from the consumer')
     .with_request('post', f'/users', body=expected)
     .will_respond_with(200, body=expected))

    with pact:
        result = create_random_users(1)

    assert len(result) == 1
