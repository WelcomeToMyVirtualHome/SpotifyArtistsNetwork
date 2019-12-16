from artist import Artist
from pyfy import ClientCreds, Spotify, excs
from time import sleep
from collections import defaultdict
import pandas as pd
import pickle
import pathlib
import config

class ArtistData:
    artist_path = r'data/%s/artists_l%d'
    adjacency_path = r'data/%s/adjacency_l%d'
    tracks_path = r'data/%s/tracks_l%d'

    def __init__(self, name, depth):
        self._depth = depth
        self._adjacency = defaultdict(list)
        self._artists = dict()
        self._tracks = pd.DataFrame()
        self._root = None
        self._name = name

    def __str__(self):
        s = ''
        for key, item in self._adjacency.items():
            s +=  self._artists[key]['name']
            s += ' <--> '
            s += ', '.join([self._artists[i]['name'] for i in item])
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
    def tracks(self):
        return self._tracks

    @property
    def depth(self):
        return self._depth

    @property
    def name(self):
        return self._name

    def download_data(self, spotify_credentials, force=False):
        '''
        Download artist with specified name. 
        If depth > 0 downloads related artists to given artist in iterations.

        :param spotify_credentials: tuple with id and key to Spotify Web API 
        :type spotify_credentials: tuple of strings
        :param force: should data be re-downloaded if it already exists in default directory
        :type force: boolean
        '''
        creds = ClientCreds(client_id=spotify_credentials[0], client_secret=spotify_credentials[1])
        self._client = Spotify(client_creds=creds)
        self._client.authorize_client_creds()
        print('Downloading artists')

        result = self._client.search(q=self._name, types='artist', limit=1)
        if len(result['artists']['items']) == 0:
            raise NameError(f'No artist with name: {self._name}.')

        self._root = Artist(result['artists']['items'][0], depth=0)
        self._adjacency[self._root.id] = []
        self._artists[self._root.id] = self._root.get_dict()
        
        if self._depth < 0:
            raise ValueError('Depth must be positive integer')

        if self._depth == 0:
            print('0 nearest neighbors')
            return

        if self._root is None:
            raise NameError(f'No data retrieved for {self._name}.')
        
        existing_depth = -1
        if not force:
            name = self._name.replace(' ', '')
            for i in range(0, self._depth + 1):
                p1 = pathlib.Path(self.artist_path % (name, i))
                p2 = pathlib.Path(self.adjacency_path % (name, i))
                if p1.exists() and p2.exists():
                    existing_depth = i
            
            if existing_depth > -1:
                if existing_depth == self._depth:
                    print("Data already exists")
                    return
                elif existing_depth < self.depth:
                    self.load_artists(existing_depth)
                    self.load_adjacency(existing_depth)
                    print(f'Loaded data: l_{existing_depth}')
            else:
                print("No artist, adjacency data downloaded")
            
            if self.adjacency is None or self.artists is None:
                existing_depth = 0

        for i in range(existing_depth + 1, self._depth + 1):
            print(f'{i} nearest neighbors')
            for id in list(self._artists):
                self.add_related(id, i)
        
        for key in self.adjacency.keys():
            self._adjacency[key] = list(set(self.adjacency[key]))
        
        
    def add_related(self, id, depth):
        '''
        Add to _adjacency list _artists related to artist with name given by name parameter.

        Function sleeps with each call for 0.1s to avoid flooding Spotify API.

        Function searches id of artist by sending a query to API. Then is queries for 
        related _artists of artist with retreived id. Adds related _artists to to list of said artist.
        Adds new _artists to dict.

        :param id: id of artist
        :type id: string
        :param depth: number of iterations of getting related artists. Not equal to depth of network.
        :type depth: int
        :return
        '''
        try:
            related = self._client.artist_related_artists(artist_id=id)
            new_artists = [Artist(r, depth) for r in related['artists']]
            
            # Append related artists to artist with given id
            self._adjacency[id].extend([a.id for a in new_artists])
        
            new_artists = [a for a in new_artists if a.id not in self._artists]
            new_artists_dict = {a.id: a.get_dict() for a in new_artists}
            self._artists = {**self._artists, **new_artists_dict}

            for a in new_artists:
                if a.id not in self._adjacency:
                    self._adjacency[a.id] = [id]
            sleep(0.2)
        except excs.ApiError as e:
            print('Error')
            print(e.msg)
    

    def download_tracks(self, spotify_credentials, force=False):
        '''
        Download top tracks features of every artist in self._artists

        :param spotify_credentials: tuple with id and key to Spotify Web API 
        :type spotify_credentials: tuple of strings
        :param force: should data be re-downloaded if it already exists in default directory
        :type force: boolean
        '''
        creds = ClientCreds(client_id=spotify_credentials[0], client_secret=spotify_credentials[1])
        self._client = Spotify(client_creds=creds)
        self._client.authorize_client_creds()
        print('Downloading tracks')

        existing_depth = -1
        artists = None
        if not force:
            name = self._name.replace(' ', '')
            for i in range(0, self._depth + 1):
                p = pathlib.Path(self.tracks_path % (name, i))
                if p.exists():
                    existing_depth = i
            
            self.load_artists(self.depth)
            
            if existing_depth > -1:
                if existing_depth == self._depth:
                    print("Data already exists - loading data")
                    self.load_tracks(existing_depth)
                    return
                elif existing_depth < self.depth:
                    self.load_tracks(existing_depth)
                    print(f'Loaded data: l_{existing_depth}')   
            else:
                print("No track data downloaded")
                        
            if self.tracks is not None:            
                artists = {key: item for key, item in self.artists.items() if item['depth'] > existing_depth}
                # artist_tracks = set(self.tracks[self.tracks['artist'] not in artists]['artist'])
            else:
                artists = self.artists
        else:
            artists = self.artists
        
        tracks = []
        try:
            for artist in artists:
                name = artists[artist]['name']
                print(f'Downloading top tracks info for {name}')
                artist_tracks = self._client.artist_top_tracks(artist, country='US')
                # Check if there are any tracks available for current artist
                if artist_tracks['tracks']:
                    tracks_features = self._client.tracks_audio_features([t['id'] for t in artist_tracks['tracks']])
                    if tracks_features:
                        # Check if there are multiple tracks
                        if 'audio_features' in tracks_features:
                            tracks_features = tracks_features['audio_features']
                        # Add to each track features an id of current artist
                        if isinstance(tracks_features, list):
                            for i in range(len(tracks_features)):
                                if tracks_features[i]:
                                    tracks_features[i]['artist'] = artist
                                else:
                                    tracks_features[i] = {'artist': artist}
                        elif isinstance(tracks_features, dict):
                            tracks_features['artist'] = artist
                            tracks_features = [tracks_features]
                else:
                    tracks_features = [{'artist': artist}]
                tracks.extend(tracks_features)
                sleep(0.2)
        except excs.ApiError as e:
            print('Error')
            print(e.msg)
            
        df = pd.DataFrame(tracks)
        df = df.drop(['analysis_url', 'track_href', 'type', 'uri'], axis='columns')
        if self.tracks is not None:
            df = df.append(self.tracks)
        self._tracks = df
        if set(self.tracks['artist']) == set(self.artists):
            print("Download successful")
        else:
            diff = set(self.tracks['artist']) - set(self.artists)
            print(f'Missing top tracks for {diff}')
            raise ValueError('Top track features not downloaded for all artists')
            
    def load_pickle(self, filename):
        if pathlib.Path(filename).exists():    
            with open(filename, 'rb') as infile:
                return pickle.load(infile)
        else:
            raise ValueError(f"{filename} doesn't exist")
            
    def load_tracks(self, depth=None):
        if depth is None:
            depth = self._depth
        name = self._name.replace(' ', '')
        self._tracks = self.load_pickle(self.tracks_path % (name, depth))
    
    def load_adjacency(self, depth=None):
        if depth is None:
            depth = self._depth
        name = self._name.replace(' ', '')
        self._adjacency = self.load_pickle(self.adjacency_path % (name, depth))

    def load_artists(self, depth=None):
        if depth is None:
            depth = self._depth
        name = self._name.replace(' ', '')
        self._artists = self.load_pickle(self.artist_path % (name, depth))
       
    def load_data(self, depth=None):
        self.load_adjacency(depth)
        self.load_artists(depth)
        self.load_tracks(depth)

    def save_pickle(self, obj, filename):
        if obj is None:
            return

        path = '/'.join(filename.split('/')[:-1])
        p = pathlib.Path(path)
        if not p.exists():
            p.mkdir()
        
        with open(filename, 'wb') as outfile:
            pickle.dump(obj, outfile)
    
    def save_tracks(self, depth=None):
        if depth is None:
            depth = self._depth
        name = self._name.replace(' ', '')
        self.save_pickle(self._tracks, self.tracks_path % (name, depth))

    def save_adjacency(self, depth=None):
        if depth is None:
            depth = self._depth
        name = self._name.replace(' ', '')
        self.save_pickle(self._adjacency, self.adjacency_path % (name, depth))
        
    def save_artists(self, depth=None):
        if depth is None:
            depth = self._depth
        name = self._name.replace(' ', '')
        self.save_pickle(self._artists, self.artist_path % (name, depth))
   
    def save_data(self, depth=None):
        self.save_adjacency(depth)
        self.save_artists(depth)    
        self.save_tracks(depth)

if __name__ == '__main__':
    d = ArtistData('Giuseppe Verdi', depth=5)
    creds = (config.CLIENT_ID, config.CLIENT_SECRET)
    # d.download_data(spotify_credentials=creds)
    # d.save_adjacency()
    # d.save_artists()
    
    d.load_artists()
    d.download_tracks(spotify_credentials=creds)
    d.save_tracks()