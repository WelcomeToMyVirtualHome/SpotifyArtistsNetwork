from artist_data import ArtistData
import config

if __name__ == '__main__':
    d = ArtistData('Giuseppe Verdi', level=3)
    # d.download_data(spotify_credentials=(config.CLIENT_ID, config.CLIENT_SECRET))
    
    d.load_data()
    # d.save_data()

    print(str(d))
    print(f'Number of artists = {len(d)}')