import os


def load_env_variable(var_name: str, default_value=None, required: bool = False):
    """
    Load an environment variable.

    Args:
        var_name (str): The name of the environment variable.
        default_value (any): The default value to return if the variable is not found.
        required (bool): Whether the variable is required. Raises an exception if True and the variable is not found.

    Returns:
        str: The value of the environment variable, or the default value if not found.

    Raises:
        ValueError: If the variable is required but not found.
    """
    value = os.getenv(var_name, default_value)
    if required and value is None:
        raise ValueError(f"Required environment variable '{var_name}' is not set.")
    return value
