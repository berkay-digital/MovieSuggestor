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
    try:
        if isinstance(genre, str) and genre.isdigit():
            genre = int(genre)

        genre_id = genre if isinstance(genre, int) else None

        if not genre_id:
            print(f"Invalid genre: {genre}")
            return []

        genre_id_str = str(genre_id)
        current_year = 2024

        # Different options for movies and TV shows with stricter filters
        if media_type == 'movie':
            discovery_options = [
                {   # Mix of popular and recent movies
                    'sort_by': 'popularity.desc',
                    'vote_count__gte': 300,
                    'primary_release_date__gte': '2015-01-01',
                    'with_original_language': 'en',
                    'page': 1
                },
                {   # Highly rated movies
                    'sort_by': 'vote_average.desc',
                    'vote_count__gte': 1000,
                    'vote_average__gte': 7.0,
                    'primary_release_date__gte': '2010-01-01',
                    'with_original_language': 'en',
                    'page': 1
                }
            ]
        else:  # TV shows
            discovery_options = [
                {   # Mix of popular and recent shows
                    'sort_by': 'popularity.desc',
                    'vote_count__gte': 300,
                    'first_air_date__gte': '2015-01-01',
                    'with_original_language': 'en',
                    'page': 1
                },
                {   # Highly rated shows
                    'sort_by': 'vote_average.desc',
                    'vote_count__gte': 500,
                    'vote_average__gte': 7.5,
                    'first_air_date__gte': '2010-01-01',
                    'with_original_language': 'en',
                    'page': 1
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
                        # Filter out items with very low popularity
                        filtered_results = [
                            item for item in results_list 
                            if item.popularity > 50 and item.vote_count >= 100
                        ]
                        # Take more results from each query
                        all_results.extend(filtered_results[:10])

            except Exception as e:
                print(f"Error with options={options}: {str(e)}")
                continue

        seen_ids = set()
        unique_results = []
        for item in all_results:
            if item.id not in seen_ids:
                seen_ids.add(item.id)
                unique_results.append(item)

        # Custom sorting that considers multiple factors
        def get_score(item):
            # Base score from rating and popularity
            score = (item.vote_average * 0.4) + (min(item.popularity, 1000) / 1000 * 0.3)
            
            # Bonus for higher vote counts (max bonus of 0.2)
            vote_count_bonus = min(item.vote_count / 10000, 0.2)
            score += vote_count_bonus
            
            # Bonus for recency (max bonus of 0.1)
            try:
                year = int(item.release_date.year if hasattr(item, 'release_date') else 
                          item.first_air_date.year if hasattr(item, 'first_air_date') else 
                          2000)
                recency_bonus = ((year - 2000) / (current_year - 2000)) * 0.1
                score += max(0, recency_bonus)
            except:
                pass
            
            return score

        # Sort results by custom score
        sorted_results = sorted(unique_results, key=get_score, reverse=True)

        # Return up to 10 results
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