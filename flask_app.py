import os
from flask import Flask, render_template, request
from spotipy import spotipy
from spotipy.spotipy.oauth2 import SpotifyClientCredentials

app = Flask(__name__)

# Get sensitive information from enviroment variables
C_ID = os.environ.get('C_ID')
C_SECRET = os.environ.get('C_SECRET')

client_credentials_manager = SpotifyClientCredentials(client_id=C_ID, client_secret=C_SECRET)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)


def get_all_playlist_tracks(user):
        usr_playlists = sp.user_playlists(user)

        tracks = []

        for up in usr_playlists['items']:
            try:
                tks = sp.user_playlist_tracks(user, playlist_id=up['id'])
                for track in tks['items']:
                        tracks.append({ 'song_name' : track['track']['name'],
                                                        'img' : track['track']['album']['images'][1]['url'],
                                                        'artists' : [ dic['name'] for dic in track['track']['artists'] ]})
            except:
                    pass

        return tracks


def find_common_tracks(tr1, tr2):
        """ params: a list of tracks """
        # Finding the smaller list of the two for optimization
        s_list = sorted([tr1, tr2], key=len)

        track_names = [item['song_name'] for item in s_list[0]]

        tracks = []

        for item in s_list[1]:
                if item['song_name'] in track_names:
                        tracks.append(item)

        return list({v['song_name']:v for v in tracks}.values())


@app.route('/', methods=['GET'])
def my_form_query():
    user_1 = request.args.get("usr1")
    user_2 = request.args.get("usr2")

    # Don't want to compare the same user, returns all songs
    # which can take long to process, also, what's the point?
    if all((user_1, user_2)) and user_1 == user_2:
        return render_template('index.html',
                msg="You should find someone to compare songs with.")

    try:
        user_one_tracks = get_all_playlist_tracks(user_1)
        user_two_tracks = get_all_playlist_tracks(user_2)
    except Exception, e:
        if "Invalid username" in str(e):
            return render_template('index.html',
                    msg="Woops. Invalid Spotify username.")
        else:
            return render_template('index.html',
                    msg="You broke it :(")


    final_list = find_common_tracks(user_one_tracks, user_two_tracks)

    if all((user_1, user_2)):
        return render_template("index.html", result=final_list, users=(user_1, user_2))

    return render_template('index.html')


if __name__ == "__main__":
    app.run('127.0.0.1')
