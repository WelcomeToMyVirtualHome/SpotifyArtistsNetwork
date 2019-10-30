from pyvis.network import Network
from data import Data

class Vis:
    def __init__(self, artists, adjacency):
        self.artists = artists
        self.adjacency = adjacency
        self.network = Network(height="1500px", width="1500px")

    def init_network(self):
        print(self.artists)
        id  = list(self.artists.keys())
        
        label = [a["name"] for _, a in self.artists.items()]
        size = [a["popularity"] for _, a in self.artists.items()]

        self.network.add_nodes(id, label = label, size = size)

        [self.network.add_edges([(key, v) for v in value]) for key, value in self.adjacency.items()]
    
    def show_network(self):
        self.network.show("net.html")

if __name__ == '__main__':
    artists = Data.load_data("artists_l5.json")
    adjacency = Data.load_data("adjacency_l5.json")
    v = Vis(artists, adjacency)
    v.init_network()
    v.show_network()