class Artist:
    def __init__(self, api_dict, depth):
        self._name = api_dict["name"]
        self._id = api_dict["id"]
        self._popularity = api_dict["popularity"]
        self._followers = api_dict["followers"]["total"]
        self._genres = api_dict["genres"]
        self._depth = depth

    @property
    def id(self):
        return self._id

    def get_dict(self):
        _dict = {
        "id" : self._id,
        "name" : self._name,
        "popularity" : self._popularity,
        "followers" : self._followers,
        "genres" : self._genres,
        "depth" : self._depth}
        return _dict
    
    def __str__(self):
        return f'''Name = {self._name}
        Id = {self._id}
        Popularity = {self._popularity}
        Followers = {self._followers}
        Genres = {self._genres}'''

