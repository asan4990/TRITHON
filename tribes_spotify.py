# Spotify Function for TRIBES
import tribes_settings, tribes_socket, math
import spotipy, psutil, time, urllib.request
from spotipy.oauth2 import SpotifyOAuth
from PIL import Image, ImageOps
from threading import Timer

# Set spotify scope
scope = "user-read-currently-playing user-modify-playback-state"

client_id = ""
client_secret = ""
redirect_uri = "http://localhost:9000"


# Authentication setup
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))


class RepeatTimer(Timer):
    def run(self):
        while not self.finished.wait(self.interval):
            self.function(*self.args, **self.kwargs)

class SpotifyTribes:

    def __init__(self):
        self.current_pos_thread = RepeatTimer(1, self.spotify_get_pos) if self.is_spotify_running() else None
        self.next_track = RepeatTimer(1, self.check_next_track) if self.is_spotify_running() else None
        self.is_playing = self.spotify_get_state() if self.is_spotify_running() else None

    def is_spotify_running(self) -> bool:
        return "Spotify.exe" in (
            p.name() for p in psutil.process_iter(attrs=["pid", "name"])
        )

    def spotify_get_pos(self):
        if 'Playing' in self.is_playing:
            while True:
                cur_time = self.spotify_get_current_pos()
        
                tribes_socket.tribes_socket.send_to_tribes(
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
        song_state = self.is_playing

        # Talk to tribes
        tribes_socket.tribes_socket.send_to_tribes(
            f'eval("GetSongData(\\"{artists}\\", \\"{song_name}\\", \\"{song_dur}\\", \\"{song_state}\\");");' + "\n"
        )
        tribes_socket.tribes_socket.send_to_tribes(
            'eval("Schedule::Add(\\"SpotifyHUD::Cover();SpotifyHUD::UpdateTitle();\\", 1.0);");'
        )
        
        # Get song duration
        # Start next track thread
        if not self.next_track.is_alive():
            try:
                self.next_track.start()
            except RuntimeError as e:
                print(e)
        
        if not self.current_pos_thread.is_alive():
            try:
                self.current_pos_thread.start()
            except RuntimeError as e:
                print(e)

    def spotify_playpause(self):
        if self.is_playing is not None:
            if self.is_spotify_running:
                sp.pause_playback()
            else:
                sp.start_playback()
                self.spotify_tribes_data()

    def spotify_next(self):
        if self.is_playing is not None:
            if self.is_spotify_running:
                sp.next_track()
                self.spotify_tribes_data()

    def spotify_prev(self):
        if self.is_playing is not None:
            if self.is_spotify_running:
                sp.previous_track()
                self.spotify_tribes_data()

    def spotify_get_current_pos(self):
        results = sp.currently_playing(market="US", additional_types="track")

        pos_mins, pos_secs = divmod(int(results["progress_ms"]) // 1000, 60)
        track_pos = f"{pos_mins}:{pos_secs:02d}"

        return track_pos
        
    def spotify_get_track_id(self):
        results = sp.currently_playing(market="US", additional_types="track")

        current_track_info = {
            "id": results["item"]["artists"][0]["id"]
        }

        return current_track_info
    
    def spotify_get_state(self):
        try:
            results = sp.currently_playing(market="US", additional_types="track")
            return "Playing" if results["is_playing"] else "Paused"
        except TypeError:
            print("Problem!")

    def spotify_get_metadata(self):
        if self.is_spotify_running():
            # Gather results
            results = sp.currently_playing(market="US", additional_types="track")

            if results is not None:
                # Track information
                #track_id = results["item"]["artists"]["id"]
                track_id = results["item"]["artists"][0]["id"]
                song = results["item"]["name"]
                #play_state = results["is_playing"]
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
                    "artists": artists_names,
                    "album_art": album_art,
                }

                return current_track_info

    def check_next_track(self):
        current_track_id = None

        if self.is_spotify_running():
            while True:
                current_track_info = self.spotify_get_track_id()
                
                if current_track_info["id"] != current_track_id:
                    self.spotify_tribes_data()
                    tribes_socket.tribes_socket.send_to_tribes(
                        'eval("SpotifyHUD::UpdateTitle();SpotifyHUD::Cover();");'
                    )
                current_track_id = current_track_info["id"]
                
                time.sleep(1)
            