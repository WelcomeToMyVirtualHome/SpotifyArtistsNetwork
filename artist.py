class Artist:
    def __init__(self, api_dict):
        self.name = api_dict["name"]
        self.id = api_dict["id"]
        self.popularity = api_dict["popularity"]
        self.followers = api_dict["followers"]["total"]
        self.genres = api_dict["genres"]

    def get_dict(self):
        _dict = {"name" : self.name,
        "popularity" : self.popularity,
        "followers" : self.followers,
        "genres" : self.genres}
        return _dict
    
    def print(self):
        print(f'''Name = {self.name}\nId = {self.id}\nPopularity = {self.popularity}\nFollowers = {self.followers}\nGenres = {self.genres}''')

