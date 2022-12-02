"""
Common functions to manage the GraphQL API
"""
import requests

from tenacity import retry, stop_after_attempt, wait_random

from codiga import constants
from codiga.common import log
from codiga.constants import API_TOKEN_HEADER, GRAPHQL_ENDPOINT_STAGING_URL, \
    GRAPHQL_ENDPOINT_PROD_URL, USER_AGENT_HEADER, USER_AGENT_CLI


@retry(stop=stop_after_attempt(7), wait=wait_random(min=1, max=2))
def do_graphql_query(api_token, payload):
    """
    Do a GraphQL query. This base method is used by all other methods that do a GraphQL query.

    :param api_token: the API token to access the GraphQL API
    :param payload: the payload we want to send.
    :return: the returned JSON object
    """
    headers = {API_TOKEN_HEADER: api_token, USER_AGENT_HEADER: USER_AGENT_CLI}
    response = requests.post(constants.GRAPHQL_ENDPOINT_PROD_URL, json=payload, headers=headers, timeout=10)
    if response.status_code != 200:
        log.error('Failed to send GraphQL query to Codiga API')
        return None
    response_json = response.json()
    return response_json["data"]


@retry(stop=stop_after_attempt(7), wait=wait_random(min=1, max=2))
def do_graphql_query_with_api_token(api_token, payload, use_staging=False):
    """
    Do a GraphQL query. This base method is used by all other methods that do a GraphQL query.

    :param api_token: the API token to access the GraphQL API
    :param payload: the payload we want to send.
    :param use_staging: use the staging endpoint
    :return: the returned JSON object
    """
    headers = {API_TOKEN_HEADER: api_token, USER_AGENT_HEADER: USER_AGENT_CLI}
    endpoint = GRAPHQL_ENDPOINT_PROD_URL
    if use_staging:
        endpoint = GRAPHQL_ENDPOINT_STAGING_URL
    response = requests.post(endpoint, json=payload, headers=headers)
    if response.status_code != 200:
        log.error('Failed to send GraphQL query to Codiga API')
        return None
    response_json = response.json()
    return response_json["data"]

@retry(stop=stop_after_attempt(7), wait=wait_random(min=1, max=2))
def do_graphql_query_with_api_token_complete(api_token, payload, use_staging=False):
    """
    Do a GraphQL query. This base method is used by all other methods that do a GraphQL query.

    :param api_token: the API token to access the GraphQL API
    :param payload: the payload we want to send.
    :param use_staging: use the staging endpoint
    :return: the returned JSON object
    """
    headers = {API_TOKEN_HEADER: api_token, USER_AGENT_HEADER: USER_AGENT_CLI}
    endpoint = GRAPHQL_ENDPOINT_PROD_URL
    if use_staging:
        endpoint = GRAPHQL_ENDPOINT_STAGING_URL
    response = requests.post(endpoint, json=payload, headers=headers)
    if response.status_code != 200:
        log.error('Failed to send GraphQL query to Codiga API')
        return None
    response_json = response.json()
    return response_json