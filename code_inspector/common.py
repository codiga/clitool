import logging
import requests
import code_inspector.constants as constants

log = logging.getLogger('code-inspector')

def do_graphql_query(access_key, secret_key, payload):
    """
    Do a GraphQL query
    :param access_key: the access key
    :param secret_key: the secret key
    :param payload: the payload we want to send.
    :return: the returned JSON object
    """
    headers = {"X-Access-Key": access_key,
               "X-Secret-Key": secret_key}
    response = requests.post(constants.GRAPHQL_ENDPOINT_URL, json=payload, headers=headers)
    if response.status_code != 200:
        log.info('Failed to send payload')
        return None
    response_json = response.json()
    return response_json["data"]
