from themoviedb import TMDb
from dotenv import load_dotenv
import os

load_dotenv()

## API ##
API_KEY = os.getenv('API_KEY')
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
        poster_url = f"https://image.tmdb.org/t/p/original{movie.poster_path}"

        return {
            'id': movie.id,
            'title': movie.title,
            'category': [genre.name for genre in movie.genres],
            'release_date': movie.release_date,
            'vote_average': movie.vote_average,
            'cast': cast,
            'overview': movie.overview,
            'poster_path': movie.poster_path,
            'poster_url': poster_url,
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
        poster_url = f"https://image.tmdb.org/t/p/original{tv.poster_path}"

        return {
            'id': tv.id,
            'title': tv.name,
            'category': [genre.name for genre in tv.genres],
            'release_date': tv.first_air_date,
            'vote_average': tv.vote_average,
            'cast': cast,
            'overview': tv.overview,
            'poster_path': tv.poster_path,
            'poster_url': poster_url,
            'media_type': 'tv'
        }
    except Exception as e:
        print(f"Error fetching TV series details: {e}")
        return {}


def get_genre_id(tmdb: TMDb, genre_name: str, media_type: str = 'movie'):
    """
    function fpr for getting genre id as its required for api
    returns genre id of movie or series
    """
    try:
        if media_type == 'movie':
            genres = tmdb.genres().movie()
        else:
            genres = tmdb.genres().tv()

        for genre in genres:
            if genre.name.lower() == genre_name.lower():
                return genre.id
        return None

    except Exception as e:
        print(f"Error getting genre ID: {e}")
        return None


def get_popular_by_genre(tmdb, genre, media_type='movie', include_adult=False):
    """"
    function for getting popular by genre
    returning dict of popular movies or series
    """
    try:
        if isinstance(genre, str) and genre.isdigit():
            genre = int(genre)

        genre_id = genre if isinstance(genre, int) else None

        if not genre_id:
            print(f"Invalid genre: {genre}")
            return []

        genre_id_str = str(genre_id)

        discovery_options = [
            {
                'sort_by': 'popularity.desc',
                'vote_count__gte': 100,
                'page': 1
            },
            {
                'sort_by': 'vote_average.desc',
                'vote_count__gte': 100,
                'vote_count__lte': 1000,
                'page': 2
            },
            {
                'sort_by': 'primary_release_date.desc' if media_type == 'movie' else 'first_air_date.desc',
                'vote_count__gte': 50,
                'page': 3
            }
        ]

        all_results = []

        for options in discovery_options:
            try:
                if media_type == 'movie':
                    params = {
                        'with_genres': genre_id_str,
                        'include_adult': include_adult,
                        **options
                    }
                    results = tmdb.discover().movie(**params)
                else:
                    params = {
                        'with_genres': genre_id_str,
                        **options
                    }
                    results = tmdb.discover().tv(**params)

                if results:
                    results_list = list(results) if not isinstance(results, list) else results
                    if results_list:
                        all_results.extend(results_list[:5])

            except Exception as e:
                print(f"Error with options={options}: {str(e)}")
                continue

        seen_ids = set()
        unique_results = []
        for item in all_results:
            if item.id not in seen_ids:
                seen_ids.add(item.id)
                unique_results.append(item)

        sorted_results = sorted(
            unique_results,
            key=lambda x: (x.vote_average * 0.7 + (x.popularity / 100) * 0.3),
            reverse=True
        )

        return sorted_results[:10]

    except Exception as e:
        print(f"Error getting popular {media_type} in genre {genre}: {str(e)}")
        return []


# You can run this file to test the api
if __name__ == "__main__":
    get_popular_by_genre(tmdb, 'comedy', media_type='movie')
    print(get_id_by_title(tmdb=tmdb, title='Levels', media_type='movie'))
    print(get_movie_details(tmdb=tmdb, movie_id=791042))
    print(get_id_by_title(tmdb=tmdb, title='outlander', media_type='tv'))
    print(get_tv_details(tmdb=tmdb, tv_id=56570))