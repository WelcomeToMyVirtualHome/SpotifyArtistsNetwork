from artist_data import ArtistData
import numpy as np
import igraph

class Network:
    def __init__(self, data):
        self._data = data
        self._graph = igraph.Graph()
      
    def graph(self):
        return self._graph

    def init(self):
        self._graph.add_vertices(list(self._data.artists.keys()))
    
        edges = [(max(key, i), min(key, i)) for key, item in self._data.adjacency.items() for i in item]
        edges = list(set(edges))
        self._graph.add_edges(edges)
        
        self._graph.vs['name'] = [item['name'] for item in self._data.artists.values()]
        self._graph.vs['followers'] = [item['followers'] for item in self._data.artists.values()]
        self._graph.vs['popularity'] = [item['popularity'] for item in self._data.artists.values()]
        self._graph.es['popularity'] = [(self._data.artists[edge[0]]['popularity'] + self._data.artists[edge[1]]['popularity']) / 2 for edge in edges]
        
    def draw(self, layout_name='large', file_format='pdf'):
        '''
        Draw created artists graph. Showing labels only for artists with popularity in 0.9 quantile.

        param: layout_name: name of algorithm to use for layout. Available options: see igraph documentation
        type: layout_name: str
        param: file_format: name of format to which graph should be saved
        type: file_format: str 
        '''
        visual_style = {}
        visual_style['edge_width'] = [item/50 for item in self._graph.es['popularity']]
        visual_style['vertex_color'] = [[0, 1, 0, 0.9] if item['name'] == self._data.name else [1, 0, 0, 0.4] for item in self._data.artists.values()]
        quantile = np.quantile([item['popularity'] for item in self._data.artists.values()], 0.95)        
        visual_style['vertex_label'] = [item['name'] if item['popularity'] > quantile or item['name'] == self._data.name else '' for item in self._data.artists.values()]
        visual_style['vertex_label_size'] = [20 if item['name'] == self._data.name else 7 for item in self._data.artists.values()]
        visual_style['vertex_label_color'] = [[0, 1, 0, 1] if item['name'] == self._data.name else [0, 0, 0, .8] for item in self._data.artists.values()]
        visual_style['vertex_size'] = [item/5 for item in self._graph.vs['popularity']]
       
        name = self._data.name.replace(' ', '')
        igraph.plot(
            self._graph,
            f'data/{name}/net_l{self._data.depth}.{file_format}',
            **visual_style,
            order=list(self._data.artists.keys()).reverse(),
            vertex_frame_width=.1,
            layout=self._graph.layout(layout_name),
            bbox=(1000,1000),
            autocurve=True)
        
if __name__ == '__main__':
    data = ArtistData('Giuseppe Verdi', depth=3)
    data.load_adjacency()
    data.load_artists()

    n = Network(data)
    n.init()
    n.draw(file_format='png')
