from typing import Any, Optional


def create_response(status_code: int, message: str, data: Optional[Any| None] ) -> dict:
    """
    Create a standardized response dictionary.

    Args:
        status_code (int): The status of the response ('success' or 'error').
        message (str): A message describing the response.
        data (dict, optional): Additional data to include in the response.

    Returns:
        dict: A dictionary containing the response.
    """
    response = {
        "status": status_code,
        "message": message,
    }
    if data is not None:
        response["data"] = data
    return response