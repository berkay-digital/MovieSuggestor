from themoviedb import TMDb
from dotenv import load_dotenv
import os

load_dotenv()

tmdb = TMDb(key=os.getenv("TMDB_API_KEY"), language="en-US", region="US")


# top rated movies 
movies = tmdb.movies().top_rated()
for movie in movies:
    print(movie)

# discover
movies = tmdb.discover().movie(
    sort_by="vote_average.desc",
    primary_release_date__gte="1997-08-15",
    vote_count__gte=10000,
    vote_average__gte=6.0,
)
for movie in movies:
    print(movie)

def get_movies_by_category(category):
    pass

# You can run this file to test the api
if __name__ == "__main__":
    get_movies_by_category("action")