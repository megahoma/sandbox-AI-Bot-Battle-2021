import logging
import os
import re
from typing import List, Union


def find_or_none(pattern: str, string: str, group_number: int) -> Union[str, None]:
    result = re.search(pattern, string)
    if result:
        return result.group(group_number)


def get_directory(path: str) -> Union[str, None]:
    return find_or_none('((?:[^/]*/)*)(.*)', path, 1)


def get_filename(path: str) -> Union[str, None]:
    return find_or_none('((?:[^/]*/)*)(.*)', path, 2)


def get_package_name(path: str) -> Union[str, None]:
    filename = get_filename(path)
    if filename:
        return find_or_none('(\w+)\.py', filename, 1)


def listdir(directory, recursive=False) -> List[str]:
    if recursive:
        a = [
            os.path.join(_dir, _file)
            for (_dir, _dirs, _files) in os.walk(directory)
            for _file in _files
        ]
        return a
    else:
        return list(map(lambda d: os.path.join(directory, d), os.listdir(directory)))


def find_all_files_with_pattern(directory: str, pattern, recursive=False) -> List[str]:
    """
    Return path to all files in given directory 
    that satisfies the pattern
    """
    allFiles = listdir(directory, recursive=recursive)
    onlyPyFiles = list(filter(lambda d: re.search(pattern, d), allFiles))

    logging.debug(
        f"Found {len(onlyPyFiles)} files in {directory} that satisfies {pattern}")
    return onlyPyFiles
