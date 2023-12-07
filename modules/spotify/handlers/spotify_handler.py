from modules.spotify.utils.spotify_utils import parse_link_to_uri
from modules.spotify.utils.spotify_utils import SpotifyAPIHelper


API_ENDPOINT = "https://api.spotify.com/v1/me/player"


def add_song_to_queue(link: str, user_name: str):
    if "track" not in link:
        print("NO TRACK URL")
        return
    url = API_ENDPOINT + "/queue"
    params = {"uri": parse_link_to_uri(link=link)}
    SpotifyAPIHelper().make_request(
        method="POST",
        url=url,
        params=params,
        user_name=user_name,
    )
