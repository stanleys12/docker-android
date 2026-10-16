import logging
import os

from typing import Union
from urllib.parse import unquote

logger = logging.getLogger("helper")


def convert_str_to_bool(given_str: str) -> bool:
    """
    Convert String to Boolean value

    :param given_str: given string
    :return: converted string in Boolean
    """
    if given_str:
        if type(given_str) is str:
            return given_str.lower() in ("yes", "true", "t", "1")
        else:
            raise AttributeError
    else:
        logger.info(f"'{given_str}' is empty!")
        return False


def get_env_value_or_raise(env_key: str) -> str:
    """
    Get value of necessary environment variable.

    :param env_key: given environment variable
    :return: env_value in String
    """
    try:
        env_value = os.getenv(env_key)
        if not env_value:
            raise RuntimeError(f"'{env_key}' is missing.")
        elif env_value.isspace():
            raise RuntimeError(f"'{env_key}' contains only white space.")
        return env_value
    except TypeError as t_err:
        logger.error(t_err)


def symlink_force(source: str, target: str) -> None:
    """
    Create Symbolic link

    :param source: source file
    :param target: target file
    :return: None
    """
    try:
        os.symlink(source, target)
    except FileNotFoundError as ffe_err:
        logger.error(ffe_err)
    except FileExistsError:
        os.remove(target)
        os.symlink(source, target)


def get_log_file(log_path: str, request_path: str) -> Union[str, None]:
    """
    Get absolute path of requested log file, only if it is a file inside the log directory

    :param log_path: log directory
    :param request_path: requested path
    :return: absolute path of log file or None
    """
    root = os.path.realpath(log_path)
    file_path = os.path.join(root, unquote(request_path).lstrip("/"))
    if not os.path.isfile(file_path):
        return None
    file_path = os.path.realpath(file_path)
    if os.path.commonpath([root, file_path]) != root:
        return None
    return file_path
