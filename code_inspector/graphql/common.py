"""
Common functions to manage the GraphQL API
"""
import requests

from code_inspector import constants as constants
from code_inspector.common import log


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