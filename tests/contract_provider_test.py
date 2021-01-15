import logging

from pact import Verifier

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def test_get_user_non_admin():
    verifier = Verifier(provider='UserService',
                        provider_base_url="https://21n0onwf4f.execute-api.eu-west-1.amazonaws.com/prod")

    output, _ = verifier.verify_pacts(
        './pacts/consumer-provider.json',
        verbose=False)

    assert (output == 0)
