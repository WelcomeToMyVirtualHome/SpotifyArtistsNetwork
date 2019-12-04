from pyvis.network import Network
from data import Data
import pickle

class Vis:
    def __init__(self, artists, adjacency):
        self.artists = artists
        self.adjacency = adjacency
        self.network = Network(height='1500px', width='1500px')

    def init_network(self):
        id  = list(self.artists.keys())
        
        label = [a['name'] for _, a in self.artists.items()]
        size = [a['popularity'] / 10 for _, a in self.artists.items()]

        self.network.add_nodes(id, label = label, size = size)

        [self.network.add_edges([(key, v) for v in value]) for key, value in self.adjacency.items()]
    
    def show_network(self):
        self.network.show('net.html')

if __name__ == '__main__':
    level = 3
    with open(f'data/artists/artists_l{level}', 'rb') as outfile:
        artists = pickle.load(outfile)
    with open(f'data/adjacency/adjacency_l{level}', 'rb') as outfile:
        adjacency = pickle.load(outfile)
    
    v = Vis(artists, adjacency)
    v.init_network()
    v.show_network()