import graph_tool as gt
from graph_tool import draw as dr
from collections import defaultdict
import numpy as np
import itertools
import pickle
import matplotlib.pyplot as plt
from artist_data import ArtistData

class Network:
    def __init__(self, data):
        self._data = data
        self.g = gt.Graph(directed=False)
        self.vproperites = {}

    def init(self):
        d  = {y : x for x, y in enumerate(self._data.artists.keys())}
    
        colors = [a['genres'] if a['genres'] else '' for _, a in self._data.artists.items()]
        colors = list(itertools.chain.from_iterable(colors))
        colors = np.unique(colors)
        
        edges = [sorted((key, i)) for key, item in self._data.adjacency.items() for i in item]
        edges = np.unique(edges, axis=0)
        
        self.vproperites['size'] = self.g.new_vertex_property('int')
        self.vproperites['color'] = self.g.new_vertex_property('int')
        self.vproperites['text'] = self.g.new_vertex_property('string')
        for key, item in self._data.artists.items():
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
        name = self._data.name.replace(' ', '')
        dr.graph_draw(
            self.g, 
            pos, 
            vprops=self.vproperites,
            output_size=(3000, 3000),
            vertex_pen_width=0.01,
            vertex_font_size=5,
            vertex_text_color=[0., 0., 0., 1.],
            edge_pen_width=0.1,
            output=f'data/{name}/net_l{self._data.level}.pdf'
            )

    def vertex_hist(self):
        return gt.stats.vertex_hist(self.g, deg='total')
        
if __name__ == '__main__':
    data = ArtistData('Giuseppe Verdi', level=3)
    data.load_data()

    n = Network(data)
    n.init()
    n.draw()

    v_counts, v_bins = n.vertex_hist()
    plt.hist(v_counts, bins=v_bins)
    plt.show()
