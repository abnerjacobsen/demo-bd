"""Utilities for formatting dictionary."""


def fmt_dict_key_to_camel_case(dict_key: str) -> str:
    """
    Convert a snake_case dictionary key to camelCase.

    Args:
        dict_key (str): The dictionary key in snake_case.

    Returns
    -------
        str: The key converted to camelCase.
    """
    return "".join(
        word if idx == 0 else word.capitalize() for idx, word in enumerate(dict_key.split("_"))
    )
