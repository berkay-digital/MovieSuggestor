from flask import Flask, render_template
from dotenv import load_dotenv
import os
from themoviedb import TMDb
load_dotenv()


app = Flask(__name__)

app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY')
app.config['DEBUG'] = True

@app.route('/')
def index():
    return render_template('main.html')

## API ##
API_KEY=os.getenv('API_KEY')
tmdb = TMDb(key=API_KEY, language='en', region='PL')


def get_id_by_title(tmdb: TMDb, title: str, media_type: str = 'movie'):
    """
    function for getting id based on movie or series name
    specify if its a movie or series in media_type
    returning id of movie or series
    """
    try:
        if media_type == 'movie':
            results = tmdb.search().movies(query=title)
        else:
            results = tmdb.search().tv(query=title)

        # Get first result if any exists
        if results and len(results) > 0:
            return results[0].id
        return None

    except Exception as e:
        print(f"Error finding ID for {title}: {e}")
        return None


def get_movie_details(tmdb: TMDb, movie_id: int):
    """
    function for getting info about movie
    returning dict of movie info
    """
    try:
        movie = tmdb.movie(movie_id).details()
        credits = tmdb.movie(movie_id).credits()
        cast = [actor.name for actor in credits.cast[:10]]

        return {
            'id': movie.id,
            'title': movie.title,
            'category': [genre.name for genre in movie.genres],
            'release_date': movie.release_date,
            'vote_average': movie.vote_average,
            'cast': cast,
            'overview': movie.overview,
            'poster_path': movie.poster_path,
            'media_type': 'movie'
        }
    except Exception as e:
        print(f"Error fetching movie details: {e}")
        return {}


def get_tv_details(tmdb: TMDb, tv_id: int):
    """
    function for getting info about tv
    returning dict of tv info
    """
    try:
        tv = tmdb.tv(tv_id).details()

        credits = tmdb.tv(tv_id).credits()
        cast = [actor.name for actor in credits.cast[:10]]

        return {
            'id': tv.id,
            'title': tv.name,
            'category': [genre.name for genre in tv.genres],
            'release_date': tv.first_air_date,
            'vote_average': tv.vote_average,
            'cast': cast,
            'overview': tv.overview,
            'poster_path': tv.poster_path,
            'media_type': 'tv'
        }
    except Exception as e:
        print(f"Error fetching TV series details: {e}")
        return {}


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

