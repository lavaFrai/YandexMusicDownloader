import os
import sys

from yandex_music import Client, track_short, track
import eyed3
from eyed3.id3.frames import ImageFrame
from tqdm import tqdm


def prepare_track_name(track_name):
    track_name = track_name.replace('/', '_').replace('?', '_').replace(':', '_').replace('*', '_').replace('"', '_').replace('<', '_').replace('>', '_').replace('|', '_').replace(' ', '_').replace('\\', '_')
    while "__" in track_name:
        track_name = track_name.replace("__", "_")
    return track_name


def main(token):
    eyed3.log.setLevel("ERROR")
    client: Client = Client(token).init()
    tracks = client.users_likes_tracks()
    os.makedirs("Downloads", exist_ok=True)

    for this_track_short in tqdm(tracks):
        this_track: track = this_track_short.fetch_track()
        path = "Downloads/" + prepare_track_name(this_track.title) + '.mp3'
        pathOg = "Downloads/" + prepare_track_name(this_track.title) + '.jpeg'
        # print(this_track.download_info)

        this_track.download_cover(pathOg, size='800x800')
        this_track.download(path, bitrate_in_kbps=320)

        audiofile = eyed3.load(path)
        if audiofile.tag is None:
            audiofile.initTag()
        audiofile.tag.artist = ', '.join(list(map(lambda x: x.name, this_track.artists)))
        audiofile.tag.album = ', '.join(list(map(lambda x: x.title, this_track.albums)))
        audiofile.tag.images.set(ImageFrame.FRONT_COVER, open(pathOg, 'rb').read(), 'image/jpeg')
        audiofile.tag.title = this_track.title
        audiofile.tag.save()

        os.remove(pathOg)


def print_help_and_exit():
    print("Usage: python3 main.py --token=<token>")
    print("To get your token, go to https://oauth.yandex.ru/authorize?response_type=token&client_id=23cabbbdc6cd418abb4b39c32c41195d copy token? when you be redirected.")
    print("More information about token getting: https://github.com/MarshalX/yandex-music-api/discussions/513")
    print("To use Oauth2 via web browser, --token=auto")
    exit(0)


if __name__ == "__main__":
    token = None
    if len(sys.argv) > 1:
        for arg in sys.argv[1:]:
            if arg.startswith("--token="):
                token = arg.split('=')[1]
            if arg == "--help":
                print_help_and_exit()
    if token is None:
        token = "auto"
        # print_help_and_exit()
    if token == "auto":
        token = __import__("tokenGetter").get_token()

    main(token=token)
