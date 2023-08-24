# Spotify Function for TRIBES
import tribes_settings
import spotipy, psutil, time, urllib.request
from spotipy.oauth2 import SpotifyOAuth
from PIL import Image, ImageOps
from threading import Thread

# Set spotify scope
scope = "user-read-currently-playing user-modify-playback-state"

client_id = "959073b1b85e4f10a69b09442cc305fa"
client_secret = "0b3fbb57a2274b568ad82285b1122939"
redirect_uri = "http://localhost:9000"


# Authentication setup
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))


class SpotifyTribes:

    def __init__(self):
        self.current_pos_thread = Thread(target=self.spotify_get_pos)
        self.next_track = Thread(target=self.check_next_track)

    def is_spotify_running(self):
        return "Spotify.exe" in (
            p.name() for p in psutil.process_iter(attrs=["pid", "name"])
        )

    def spotify_get_pos(self):
        data = self.spotify_get_metadata()
        is_playing = data['state']

        if 'Playing' in is_playing:
            while True:
                cur_time = self.spotify_get_current_pos()
        
                tribes_settings.tribes_socket.send_to_tribes(
                    f'eval("GetCurrentPos(\\"{cur_time}\\");");' + "\n"
                )

                time.sleep(1)

    def spotify_tribes_data(self):
        # Grab spotify data
        data = self.spotify_get_metadata()

        url = data["album_art"]
        urllib.request.urlretrieve(url, f"{tribes_settings.TRIBES_DIR}\\Spotify\\temp\\album.png")

        # Opening the image and displaying it (to confirm its presence)
        img = Image.open(f"{tribes_settings.TRIBES_DIR}\\Spotify\\temp\\album.png")
        image = ImageOps.contain(img, (84, 84))
        image.save(f"{tribes_settings.TRIBES_DIR}\\Spotify\\temp\\album1.png")

        # Get song info
        song_name = data["song"]
        artists = data["artists"]
        song_dur = data["time"]
        song_state = data["state"]

        # Talk to tribes
        tribes_settings.tribes_socket.send_to_tribes(
            f'eval("GetSongData(\\"{artists}\\", \\"{song_name}\\", \\"{song_dur}\\", \\"{song_state}\\");");' + "\n"
        )

        # Experimental (get current song pos)
        if not self.current_pos_thread.is_alive():
            self.current_pos_thread.start()
        
        if not self.next_track.is_alive():
            self.next_track.start()

    def spotify_playpause(self):
        data = self.spotify_get_metadata()
        is_playing = data["state"]

        if self.is_spotify_running and "Playing" in is_playing:
            sp.pause_playback()
        else:
            sp.start_playback()
            time.sleep(1)
            self.spotify_tribes_data()

    def spotify_next(self):
        data = self.spotify_get_metadata()
        is_playing = data["state"]

        if self.is_spotify_running and "Playing" in is_playing:
            sp.next_track()
            time.sleep(1)
            self.spotify_tribes_data()

    def spotify_prev(self):
        data = self.spotify_get_metadata()
        is_playing = data["state"]

        if self.is_spotify_running and "Playing" in is_playing:
            sp.previous_track()
            time.sleep(1)
            self.spotify_tribes_data()

    def spotify_get_current_pos(self):
        results = sp.currently_playing(market="US", additional_types="track")

        pos_mins, pos_secs = divmod(int(results["progress_ms"]) // 1000, 60)
        track_pos = f"{pos_mins}:{pos_secs:02d}"

        return track_pos

    def spotify_get_metadata(self):
        if self.is_spotify_running():
            # Gather results
            results = sp.currently_playing(market="US", additional_types="track")

            if results is not None:
                # Track information
                track_id = results["item"]["artists"][0]["id"]
                song = results["item"]["name"]
                play_state = results["is_playing"]
                artists = [artist for artist in results["item"]["artists"]]
                album_art = results["item"]["album"]["images"][0]["url"]

                # Track position & duration
                track_mins, track_secs = divmod(
                    int(results["item"]["duration_ms"]) // 1000, 60
                )
                track_time = f"{track_mins}:{track_secs:02d}"

                artists_names = ", ".join([artist["name"] for artist in artists])

                current_track_info = {
                    "id": track_id,
                    "song": song,
                    "time": track_time,
                    "state": "Playing" if play_state else "Paused",
                    "artists": artists_names,
                    "album_art": album_art,
                }

                return current_track_info
        else:
            print("Spotify is not running..")

    def check_next_track(self):
        current_track_id = None

        if self.is_spotify_running():
            while True:
                current_track_info = self.spotify_get_metadata()
                
                if current_track_info["id"] != current_track_id:
                    self.spotify_tribes_data()
                    tribes_settings.tribes_socket.send_to_tribes(
                        'eval("SpotifyHUD::Cover();SpotifyHUD::UpdateTitle();");'
                    )
    
                current_track_id = current_track_info["id"]
                
                time.sleep(1)
