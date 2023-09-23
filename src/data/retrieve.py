import gzip
import json
from io import BytesIO

from requests import Response

from src.data.type import GameData
from src.http_helper import request_game


def bytes_to_json(input_bytes: bytes) -> GameData:
    gzip_bytes = BytesIO(input_bytes)
    with gzip.GzipFile(fileobj=gzip_bytes, mode="rb") as gzipped_file:
        return json.loads(gzipped_file.read().decode('utf-8'))


def parse_response(response: Response) -> GameData:
    if response.status_code != 200:
        return None
    return bytes_to_json(response.content)


def retrieve_game(gameId: str) -> GameData:
    """
    :param gameId: id of the game that you want to retrieve the data from. Should always be valid.
    :return: GameData object for given game, None if error.
    """
    return parse_response(request_game(gameId))


if __name__ == '__main__':
    print('Invalid gameId: ', retrieve_game('24'))
    print('Valid gameId: ', retrieve_game('ESPORTSTMNT01:3394799'))
