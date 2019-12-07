from artist_data import ArtistData
from network import Network
import config
import argparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Spotify Artist Network')
    parser.add_argument('name', help='Name of artist')
    parser.add_argument('depth', help='Depth of network', default=1, type=int)    
    args = parser.parse_args()

    d = ArtistData(args.name, depth=args.depth)
    d.download_data(spotify_credentials=(config.CLIENT_ID, config.CLIENT_SECRET))
    d.save_data()

    n = Network(d)
    n.init()
    n.draw('png')