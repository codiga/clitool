from .version import __version__

GRAPHQL_ENDPOINT_PROD_URL = 'https://api.codiga.io/graphql'
GRAPHQL_ENDPOINT_STAGING_URL = 'https://api-staging.codiga.io/graphql'

DEFAULT_TIMEOUT = 600  # 20 minutes
VALID_SCM_KINDS = ["Bitbucket", "Git", "Github", "Gitlab"]

BLANK_SHA = "0000000000000000000000000000000000000000"

API_TOKEN_ENVIRONMENT_VARIABLE = "CODIGA_API_TOKEN"

API_TOKEN_HEADER = "X-Api-Token"
USER_AGENT_HEADER = "User-Agent"
USER_AGENT_CLI = f"Cli/{__version__}"