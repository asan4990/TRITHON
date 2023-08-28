# Reserved for TRITHON module
from Trithon import Trithon
trithon = Trithon()

# Add import modules that correspond to the python functions
import tribes_spotify

sp = tribes_spotify.SpotifyTribes()

# Register TRIBES and Python functions
trithon_functions = {
    # Internal
    'JsonRead': trithon.read_json,
    'JsonWrite': trithon.write_json,
    'eval': trithon.eval,

    # Spotify
    "spotifyPlay": sp.spotify_playpause,
    "spotifyNext": sp.spotify_next,
    "spotifyPrev": sp.spotify_prev,
    "spotifyGrab": sp.spotify_tribes_data
}

trithon.add_to_dict(**trithon_functions)
