from pyfy import ClientCreds, Spotify
from artist import Artist
from data import Data
from vis import Vis
import config

if __name__ == '__main__':
    client = ClientCreds(client_id=config.CLIENT_ID, client_secret=config.CLIENT_SECRET)
    spt = Spotify(client_creds=client)
    spt.authorize_client_creds()

    level = 4
    d = Data('Giuseppe Verdi', level=level, client=spt)
    d.download_data()
    
    # print(str(d))
    print(f'Number of nodes = {len(d)}')
    d.save_data()