from artist import Artist
from pyfy import excs
import networkx as nx
from time import sleep
from collections import defaultdict
import pickle

class Data:
    def __init__(self, name, level, client):
        self.level = level
        self.client = client
        self.adjacency = defaultdict(list)
        self.artists = dict()
        self.root = None

        result = self.client.search(q=name, types='artist', limit=1)
        if len(result['artists']['items']) == 0:
            print(f'No artist with name: {name}.')
            return

        self.root = Artist(result['artists']['items'][0])
        self.adjacency[self.root.id] = []
        self.artists[self.root.id] = self.root.get_dict()

    def __str__(self):
        s = ''
        for key, item in self.adjacency.items():
            s +=  self.artists[key]['name']
            s += ' <--> '
            s += ", ".join([self.artists[i]['name'] for i in item])
            s += '\n'
        return s

    def __len__(self):
        return len(self.artists)

    def download_data(self):
        if self.root is None:
            print('Cannot download data: no root')
            return

        if self.level == 0:
            print('0 nearest neighbors')
            return
        
        for i in range(self.level):
            print(f'{i + 1} nearest neighbors')
            for id in list(self.adjacency):
                self.add_related(id)
        
    def add_related(self, id):
        '''
        Add to adjacency list artists related to artist with name given by name parameter.

        Function sleeps with each call for 0.1s to avoid flooding Spotify API.

        Function searches id of artist by sending a query to API. Then is queries for 
        related artists of artist with retreived id. Adds related artists to to list of said artist.
        Adds new artists to dict.

        :param name: name of artist
        :type name: string
        :return
        '''
        try:
            related = self.client.artist_related_artists(artist_id=id)
            new_artists = [Artist(r) for r in related['artists']]
            new_artists_dict = {a.id : a.get_dict() for a in new_artists}
            self.artists = {**self.artists, **new_artists_dict}

            # Append related artists to artist with given id
            self.adjacency[id] += [a.id for a in new_artists]

            # Add related artists
            for a in new_artists:
                if a.id not in self.adjacency:
                    self.adjacency[a.id] = [id]
            sleep(0.1)
        except excs.ApiError as e:
            print('Error')
            print(e.msg)
            sleep(10)
    
    def save_data(self):
        with open(f'data/artists/artists_l{self.level}', 'wb') as outfile:
            pickle.dump(self.artist, outfile)    
        with open(f'data/adjacency/adjacency_l{self.level}', 'wb') as outfile:
            pickle.dump(self.adjacency, outfile)

    def load_data(self):
        with open(f'data/artists/artists_l{self.level}', 'rb') as infile:
            self.artists = pickle.load(infile)
        with open(f'data/adjacency/adjacency_l{self.level}', 'rb') as infile:
            self.adjacency = pickle.load(infile)

        

    
