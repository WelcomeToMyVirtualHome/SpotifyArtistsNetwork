from artist_data import ArtistData
from collections import defaultdict
from graph_tool import draw as dr
# from itertools.chain import from_iterable
import matplotlib.pyplot as plt
import graph_tool as gt
import numpy as np
import pickle

class Network:
    def __init__(self, data):
        self._data = data
        self.g = gt.Graph(directed=False)
        self.vproperites = {}

    def init(self):
        # Dictionary for mapping ids to consequent numbers
        d  = {y : x for x, y in enumerate(self._data.artists.keys())}

        # TODO: map unique genres in network to colors
        # colors = [a['genres'] if a['genres'] else '' for _, a in self._data.artists.items()]
        # colors = list(from_iterable(colors))
        # colors = np.unique(colors)
          
        self.vproperites['size'] = self.g.new_vertex_property('int')
        self.vproperites['color'] = self.g.new_vertex_property('int')
        self.vproperites['text'] = self.g.new_vertex_property('string')
        self.vproperites['font_size'] = self.g.new_vertex_property('int')
        self.vproperites['fill_color'] = self.g.new_vertex_property('vector<float>')
        self.vproperites['color'] = self.g.new_vertex_property('vector<float>')
        for _, item in self._data.artists.items():
            node = self.g.add_vertex()
            self.vproperites['size'][node] = item['popularity'] / 2
            self.vproperites['text'][node] = item['name']
            if item['name'] == self._data.name:
                self.vproperites['fill_color'][node] = [.0, 1., .0, .5]
                self.vproperites['color'][node] = [.0, 1., .0, .5]
                self.vproperites['font_size'][node] = 15
            else:
                self.vproperites['fill_color'][node] = [1., .0, .0, .5]
                self.vproperites['color'][node] = [1., .0, .0, .5]
                self.vproperites['font_size'][node] = 5
            
        edges = [sorted((key, i)) for key, item in self._data.adjacency.items() for i in item]
        edges = np.unique(edges, axis=0)
        for e in edges:
            self.g.add_edge(d[e[0]], d[e[1]])

    def draw(self, file_format='pdf'):
        # Optional available layouts
        # pos = dr.fruchterman_reingold_layout(self.g)
        # pos = dr.sfdp_layout(self.g)
        pos = dr.arf_layout(self.g)
        
        name = self._data.name.replace(' ', '')
        dr.graph_draw(
            self.g, 
            pos, 
            vorder=self.g.degree_property_map("in"),
            vprops=self.vproperites,
            output_size=(2000, 2000),
            vertex_pen_width=0.01,
            vertex_text_position=-.1,
            vertex_text_color=[0., 0., 0., 1.],
            edge_pen_width=1,
            bg_color=[1., 1., 1., 1.],
            fit_view=4.,
            output=f'data/{name}/net_l{self._data.depth}.{file_format}'
            )

    def vertex_hist(self):
        return gt.stats.vertex_hist(self.g, deg='total')
        
if __name__ == '__main__':
    data = ArtistData('Giuseppe Verdi', depth=4)
    data.load_data()

    n = Network(data)
    n.init()
    n.draw('png')

    v_counts, v_bins = n.vertex_hist()
    plt.hist(v_counts, bins=v_bins)
    plt.show()
