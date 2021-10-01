import argparse
import json
import logging
import pathlib
import time
from typing import Tuple, Union

import src.constants as constants
from src import IBot
from src.game import Game, GameOver
from src.importsTools import import_bot


def play_one_game(bot1: IBot, bot2: IBot, show=0) -> dict:
    """
    Plays game between two bots

    Return info about the game in json format
    """
    logging.debug(f"Play game between {bot1._name} and {bot2._name}")
    game = Game.default_game(bots=(bot1, bot2))

    # run game using python iterations
    gameIter = game.__iter__()
    for _ in gameIter:
        if show:
            print(
                f"Snake1: {game.bot1_runner.lastMove} \tSnake2: {game.bot2_runner.lastMove}")
            print(game)
            time.sleep(show)

    states = gameIter.getStates()
    game_description = GameOver(
        states['metadata']['winner'], states['metadata']['description']).__str__()
    logging.debug(game_description)
    if show:
        print(game_description)

    return states


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'bots', nargs=2,
        help='two paths to python files with Bot class',
    )
    parser.add_argument(
        '-s', '--show', type=float,
        help='add animation with given delay in seconds')
    parser.add_argument(
        '-o', '--output', type=pathlib.Path,
        help='path to output states of game. default is game.json',
    )

    args = parser.parse_args()
    bot1_path, bot2_path = args.bots
    bot1, bot2 = import_bot(bot1_path), import_bot(bot2_path)

    states = play_one_game(bot1, bot2, show=args.show)

    if args.output:
        with open(args.output, 'w') as file:
            json.dump(states, file, indent=4)
