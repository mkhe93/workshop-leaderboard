import os
import sys


def get_env_or_default(key, default):
    """
    Retrieve the value of an environment variable or return a default value.

    Parameters:
        key (str): The name of the environment variable to retrieve.
        default (Any): The default value to return if the environment variable is not set or is empty.

    Returns:
        Any: The value of the environment variable if set and non-empty, otherwise the default value.
    """
    val = os.environ.get(key)
    # Use default if val is None or an empty string
    if not val:
        return default
    return val


def get_api_key() -> str:
    """
    Retrieve the API key from the environment or prompt the user.

    Returns:
        str: The API key.

    Raises:
        SystemExit: If no API key is provided.
    """
    api_key = os.environ.get("LITELLM_API_KEY")
    if not api_key:
        try:
            api_key = input("Enter your Litellm API key: ").strip()
        except EOFError:
            print("No API key provided. Exiting.")
            sys.exit(1)
    if not api_key:
        print("No API key provided. Exiting.")
        sys.exit(1)
    # At this point api_key is guaranteed to be a non-empty string
    assert api_key is not None and api_key != ""
    return api_key


def get_base_url() -> str:
    """
    Retrieve the gateway base url from the environment or prompt the user.

    Returns:
        str: The base url.

    Raises:
        SystemExit: If no base url is provided.
    """
    base_url = os.environ.get("LITELLM_BASE_URL")
    print("\nLiteLLM Gateway Endpoint: ", base_url, "\n")
    if not base_url:
        try:
            base_url = input("Enter your Litellm Gateway base url: ").strip()
        except EOFError:
            print("No base url provided. Exiting.")
            sys.exit(1)
    if not base_url:
        print("No base url provided. Exiting.")
        sys.exit(1)
    # At this point base_url is guaranteed to be a non-empty string
    assert base_url is not None and base_url != ""
    return base_url
