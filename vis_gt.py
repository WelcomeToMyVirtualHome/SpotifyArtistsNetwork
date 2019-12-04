import graph_tool as gt
from graph_tool import draw as dr
from collections import defaultdict
import numpy as np
import itertools
import pickle

class Vis:
    def __init__(self, artists, adjacency):
        self.artists = artists
        self.adjacency = adjacency
        self.g = gt.Graph(directed=False)
        self.vproperites = {}

    def init(self):
        d  = {y : x for x, y in enumerate(self.artists.keys())}
    
        colors = [a['genres'] if a['genres'] else '' for _, a in self.artists.items()]
        colors = list(itertools.chain.from_iterable(colors))
        colors = np.unique(colors)
        
        edges = [sorted((key, i)) for key, item in self.adjacency.items() for i in item]
        edges = np.unique(edges, axis=0)
        
        self.vproperites['size'] = self.g.new_vertex_property('int')
        self.vproperites['color'] = self.g.new_vertex_property('int')
        self.vproperites['text'] = self.g.new_vertex_property('string')
        for key, item in self.artists.items():
            node = self.g.add_vertex()
            self.vproperites['size'][node] = item['popularity']
            # self.vproperites['text'][node] = item['name']
            self.vproperites['text'][node] =  d[key]
        
        for e in edges:
            self.g.add_edge(d[e[0]], d[e[1]])
        
    def draw(self):
        # pos = d.fruchterman_reingold_layout(self.g)
        # pos = dr.sfdp_layout(self.g)
        pos = dr.arf_layout(self.g)
        
        # dr.interactive_window(
        dr.graph_draw(
            self.g, 
            pos, 
            vprops=self.vproperites,
            output_size=(3000, 3000),
            vertex_pen_width=0.01,
            vertex_font_size=5,
            vertex_text_color=[0., 0., 0., 1.],
            edge_pen_width=0.1,
            output='img.pdf'
            )

if __name__ == '__main__':
    level = 4
    with open(f'data/artists/artists_l{level}', 'rb') as outfile:
        artists = pickle.load(outfile)
    with open(f'data/adjacency/adjacency_l{level}', 'rb') as outfile:
        adjacency = pickle.load(outfile)

    v = Vis(artists, adjacency)
    v.init()
    v.draw()