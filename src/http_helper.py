import requests

S3_BUCKET_URL = "https://power-rankings-dataset-gprhack.s3.us-west-2.amazonaws.com"
GAME_DIRECTORY = "games"


def request_game(gameId: str) -> requests.Response:
    return requests.get(f"{S3_BUCKET_URL}/{GAME_DIRECTORY}/{gameId}.json.gz")
