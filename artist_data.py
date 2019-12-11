from artist import Artist
from pyfy import excs
from pyfy import ClientCreds, Spotify
from time import sleep
from collections import defaultdict
import pickle
import pathlib
import config

class ArtistData:
    def __init__(self, name, depth):
        self._depth = depth
        self._adjacency = defaultdict(list)
        self._artists = dict()
        self._root = None
        self._name = name

    def __str__(self):
        s = ''
        for key, item in self._adjacency.items():
            s +=  self._artists[key]['name']
            s += ' <--> '
            s += ", ".join([self._artists[i]['name'] for i in item])
            s += '\n'
        return s

    def __len__(self):
        return len(self._artists)

    @property
    def artists(self):
        return self._artists
    
    @property
    def adjacency(self):
        return self._adjacency

    @property
    def depth(self):
        return self._depth

    @property
    def name(self):
        return self._name

    def download_data(self, spotify_credentials, force=False):
        creds = ClientCreds(client_id=spotify_credentials[0], client_secret=spotify_credentials[1])
        self._client = Spotify(client_creds=creds)
        self._client.authorize_client_creds()
        result = self._client.search(q=self._name, types='artist', limit=1)
        if len(result['artists']['items']) == 0:
            raise NameError(f'No artist with name: {self._name}.')

        self._root = Artist(result['artists']['items'][0], depth=0)
        self._adjacency[self._root.id] = []
        self._artists[self._root.id] = self._root.get_dict()
            
        if self._depth <= 0:
            print('0 nearest neighbors')
            return

        if self._root is None:
            raise NameError(f'No data retrieved for {self._name}.')
            
        if not force:
            name = self._name.replace(' ', '')
            existing_depth = 0
            for i in range(0, self._depth + 1):
                p1 = pathlib.Path(f'data/{name}/artists_l{i}')
                p2 = pathlib.Path(f'data/{name}/adjacency_l{i}')
                if p1.exists() and p2.exists():
                    existing_depth = i
            
            if existing_depth == self._depth:
                print('Data already exists')
                return    
            
            self.load_data(existing_depth)
            print(f'Loaded data: l_{existing_depth}')
        
        for i in range(existing_depth + 1, self._depth + 1):
            print(f'{i} nearest neighbors')
            for id in list(self._artists):
                self.add_related(id, i)
        
    def add_related(self, id, depth):
        '''
        Add to _adjacency list _artists related to artist with name given by name parameter.

        Function sleeps with each call for 0.1s to avoid flooding Spotify API.

        Function searches id of artist by sending a query to API. Then is queries for 
        related _artists of artist with retreived id. Adds related _artists to to list of said artist.
        Adds new _artists to dict.

        :param name: name of artist
        :type name: string
        :return
        '''
        try:
            related = self._client.artist_related_artists(artist_id=id)
            new_artists = [Artist(r, depth) for r in related['artists']]
            new_artists = [a for a in new_artists if a.id not in self._artists]
            new_artists_dict = {a.id : a.get_dict() for a in new_artists}
            self._artists = {**self._artists, **new_artists_dict}

            # Append related _artists to artist with given id
            self._adjacency[id] += [a.id for a in new_artists]

            for a in new_artists:
                if a.id not in self._adjacency:
                    self._adjacency[a.id] = [id]
            sleep(0.1)
        except excs.ApiError as e:
            print('Error')
            print(e.msg)
            sleep(10)
    
    def save_data(self, depth=None):
        if depth is None:
            depth = self._depth
        name = self._name.replace(' ', '')
        p = pathlib.Path(f'data/{name}')
        if not p.exists ():
            p.mkdir()
        with open(f'data/{name}/artists_l{depth}', 'wb') as outfile:
            pickle.dump(self._artists, outfile)    
        with open(f'data/{name}/adjacency_l{depth}', 'wb') as outfile:
            pickle.dump(self._adjacency, outfile)

    def load_data(self, depth=None):
        if depth is None:
            depth = self._depth
        name = self._name.replace(' ', '')
        p = pathlib.Path(f'data/{name}')
        if not p.exists ():
            raise NameError('Path does not exist')    
        with open(f'data/{name}/artists_l{depth}', 'rb') as infile:
            self._artists = pickle.load(infile)
        with open(f'data/{name}/adjacency_l{depth}', 'rb') as infile:
            self._adjacency = pickle.load(infile)

if __name__ == '__main__':
    d = ArtistData('Giuseppe Verdi', depth=5)
    d.download_data(spotify_credentials=(config.CLIENT_ID, config.CLIENT_SECRET))
    d.save_data()