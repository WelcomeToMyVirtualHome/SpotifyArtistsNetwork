from pyfy import ClientCreds, Spotify
from artist import Artist
from data import Data
from vis import Vis
import config

if __name__ == "__main__":
    client = ClientCreds(client_id = config.CLIENT_ID, client_secret = config.CLIENT_SECRET)
    spt = Spotify(client_creds = client)
    spt.authorize_client_creds()

    d = Data("Giuseppe Verdi", level = 2, client = spt)
    d.download_data()
    
    Data.save_data(d.adjacency, "adjacency_l2.json")
    Data.save_data(d.artists, "artists_l2.json")
