from artist import Artist
from pyfy import excs
import networkx as nx
from time import sleep
from collections import defaultdict
import json

class Data:
    def __init__(self, name, level, client):
        self.level = level
        self.client = client
        self.adjacency = defaultdict(list)
        self.artists = dict()
        self.root = None

        result = self.client.search(q = name, types = 'artist', limit = 1)
        if len(result["artists"]["items"]) == 0:
            print(f"No artist with name: {name}.")
            return

        self.root = Artist(result["artists"]["items"][0])
        self.adjacency[self.root.id] = []
        
        self.artists[self.root.id] = self.root.get_dict()
        
    def download_data(self):
        if self.root is None:
            print("Cannot download data: no root")
            return

        if self.level == 0:
            print("0 nearest neighbors")
            return
        
        for i in range(self.level):
            print(f"{i + 1} nearest neighbors")
            [self.add_related(id) for id in list(self.adjacency)]
        
    def add_related(self, id):
        """
        Add to adjacency list artists related to artist with name given by name parameter.

        Function sleeps with each call for 0.1s to avoid flooding Spotify API.

        Function searches id of artist by sending a query to API. Then is queries for 
        related artists of artist with retreived id. Adds related artists to to list of said artist.
        Adds new artists to dict.

        :param name: name of artist
        :type name: string
        :return
        """
        
        try:
            related = self.client.artist_related_artists(artist_id = id)
            new_artists = [Artist(r) for r in related["artists"]]
            new_artists_dict = {a.id : a.get_dict() for a in new_artists}
            self.artists = {**self.artists, **new_artists_dict}

            # Remove duplicate vertex names from list
            self.adjacency[id] = list(set(self.adjacency[id] + [a.id for a in new_artists]))

            # Dictionary of vertexes for artists related to root
            new_dict = {a.id : [id] for a in new_artists}

            # Append new dict to existing one
            self.adjacency = {**self.adjacency, **new_dict}
            sleep(0.1)
        except excs.ApiError as e:
            print("Error")
            print(e.msg)
            sleep(10)
    
    @staticmethod
    def save(data, filename):
        _json = json.dumps(data)
        f = open(filename, "w")
        f.write(_json)
        f.close()

    @staticmethod
    def load(filename):
        with open(filename) as json_file:
            data = json.load(json_file)
        return data
