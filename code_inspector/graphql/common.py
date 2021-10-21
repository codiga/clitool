"""
Common functions to manage the GraphQL API
"""
import requests

from tenacity import retry, stop_after_attempt, wait_random

from code_inspector import constants
from code_inspector.common import log


@retry(stop=stop_after_attempt(7), wait=wait_random(min=1, max=2))
def do_graphql_query(access_key, secret_key, payload):
    """
    Do a GraphQL query. This base method is used by all other methods that do a GraphQL query.

    :param access_key: the access key
    :param secret_key: the secret key
    :param payload: the payload we want to send.
    :return: the returned JSON object
    """
    headers = {"X-Access-Key": access_key,
               "X-Secret-Key": secret_key}
    response = requests.post(constants.GRAPHQL_ENDPOINT_URL, json=payload, headers=headers)
    if response.status_code != 200:
        log.error('Failed to send GraphQL query to Code Inspector API')
        return None
    response_json = response.json()
    return response_json["data"]


@retry(stop=stop_after_attempt(7), wait=wait_random(min=1, max=2))
def do_graphql_query_with_api_token(api_token, payload):
    """
    Do a GraphQL query. This base method is used by all other methods that do a GraphQL query.

    :param api_token: the API token to access the GraphQL API
    :param payload: the payload we want to send.
    :return: the returned JSON object
    """
    headers = {"X-Api-Token": api_token}
    response = requests.post(constants.GRAPHQL_ENDPOINT_URL, json=payload, headers=headers)
    print(response.json())
    if response.status_code != 200:
        log.error('Failed to send GraphQL query to Code Inspector API')
        return None
    response_json = response.json()
    return response_json["data"]