import importlib
import logging
import sys
from typing import Tuple, Union

from .bot import IBot
from .utils import get_directory, get_package_name


def import_bot(path, name=None, _id=None) -> IBot:
    """
    Import and return instance of participant bot
    """
    dirName = get_directory(path)
    packageName = get_package_name(path)
    sys.path.insert(0, dirName)
    logging.debug(f"Trying to import {packageName} from {dirName}\n{sys.path}")
    
    try:
        Bot: IBot = importlib.import_module(packageName).Bot
    except ModuleNotFoundError as e:
        raise ModuleNotFoundError(f"Import error during importing module {packageName} from {dirName}: {e}")
    
    except AttributeError:
        raise ImportError(f"Package {packageName} does not contain attribute Bot")

    # remove all info about module to prevent cheating
    sys.path.remove(dirName)
    del sys.modules[packageName]

    if not isinstance(Bot, type):
        raise ImportError(
            f"Attribute Bot in package {packageName} is not a class")

    try:
        bot = Bot(_name=name or packageName, _id=_id)

        # check if bot has all attributes from IBot
        for attr in IBot().__dict__:
            bot.__getattribute__(attr)

    except (TypeError, AttributeError) as e:
        raise ImportError(
            f"In {packageName} you need to inherit from IBot, pass *args and **kwargs in __init__ and initialize IBot subclass")

    return bot
