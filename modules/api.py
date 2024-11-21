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
    function fpr for getting genre id as it's required for api
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
        if isinstance(genre, str) and ',' in genre:
            genre_id_str = genre
        elif isinstance(genre, str) and genre.isdigit():
            genre_id_str = genre
        elif isinstance(genre, int):
            genre_id_str = str(genre)
        else:
            print(f"Invalid genre format: {genre}")
            return []

        current_year = 2024

        # Expanded discovery options for more diversity
        if media_type == 'movie':
            discovery_options = [
                {   # Recent popular movies
                    'sort_by': 'popularity.desc',
                    'vote_count__gte': 100,
                    'primary_release_date__gte': '2020-01-01',
                    'with_original_language': 'en',
                    'page': 1
                },
                {   # Highly rated movies from 2010s
                    'sort_by': 'vote_average.desc',
                    'vote_count__gte': 500,
                    'vote_average__gte': 7.0,
                    'primary_release_date__gte': '2010-01-01',
                    'primary_release_date__lte': '2019-12-31',
                    'with_original_language': 'en',
                    'page': 1
                },
                {   # Classic movies (2000s)
                    'sort_by': 'vote_average.desc',
                    'vote_count__gte': 1000,
                    'primary_release_date__gte': '2000-01-01',
                    'primary_release_date__lte': '2009-12-31',
                    'with_original_language': 'en',
                    'page': 1
                },
                {   # Hidden gems (lower vote count but high rating)
                    'sort_by': 'vote_average.desc',
                    'vote_count__gte': 100,
                    'vote_count__lte': 500,
                    'vote_average__gte': 7.5,
                    'with_original_language': 'en',
                    'page': 1
                },
                {   # Older classics
                    'sort_by': 'vote_average.desc',
                    'vote_count__gte': 500,
                    'primary_release_date__gte': '1990-01-01',
                    'primary_release_date__lte': '1999-12-31',
                    'vote_average__gte': 7.0,
                    'with_original_language': 'en',
                    'page': 1
                }
            ]
        else:  # TV shows
            discovery_options = [
                {   # Recent popular shows
                    'sort_by': 'popularity.desc',
                    'vote_count__gte': 100,
                    'first_air_date__gte': '2020-01-01',
                    'with_original_language': 'en',
                    'page': 1
                },
                {   # Highly rated shows from 2010s
                    'sort_by': 'vote_average.desc',
                    'vote_count__gte': 300,
                    'vote_average__gte': 7.5,
                    'first_air_date__gte': '2010-01-01',
                    'first_air_date__lte': '2019-12-31',
                    'with_original_language': 'en',
                    'page': 1
                },
                {   # Classic shows (2000s)
                    'sort_by': 'vote_average.desc',
                    'vote_count__gte': 500,
                    'first_air_date__gte': '2000-01-01',
                    'first_air_date__lte': '2009-12-31',
                    'with_original_language': 'en',
                    'page': 1
                },
                {   # Hidden gems
                    'sort_by': 'vote_average.desc',
                    'vote_count__gte': 50,
                    'vote_average__gte': 7.5,
                    'with_original_language': 'en',
                    'page': 2  # Use different page to get less popular items
                },
                {   # Older classics
                    'sort_by': 'vote_average.desc',
                    'vote_count__gte': 300,
                    'first_air_date__gte': '1990-01-01',
                    'first_air_date__lte': '1999-12-31',
                    'vote_average__gte': 7.0,
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
                    # Remove vote_count__lte if present for TV shows
                    tv_params = options.copy()
                    tv_params.pop('vote_count__lte', None)
                    params = {
                        'with_genres': genre_id_str,
                        **tv_params
                    }
                    results = tmdb.discover().tv(**params)

                if results:
                    results_list = list(results) if not isinstance(results, list) else results
                    if results_list:
                        # Relaxed filtering criteria
                        filtered_results = [
                            item for item in results_list 
                            if item.popularity > 20 and item.vote_count >= 50
                        ]
                        # Take fewer results from each query to ensure diversity
                        all_results.extend(filtered_results[:5])

            except Exception as e:
                print(f"Error with options={options}: {str(e)}")
                continue

        seen_ids = set()
        unique_results = []
        for item in all_results:
            if item.id not in seen_ids:
                seen_ids.add(item.id)
                unique_results.append(item)

        def get_score(item):
            # Reduced weight of popularity in scoring
            score = (item.vote_average * 0.5) + (min(item.popularity, 1000) / 1000 * 0.2)
            
            # Increased weight of vote count but with diminishing returns
            vote_count_bonus = min(item.vote_count / 5000, 0.2)
            score += vote_count_bonus
            
            try:
                year = int(item.release_date.year if hasattr(item, 'release_date') else 
                          item.first_air_date.year if hasattr(item, 'first_air_date') else 
                          2000)
                # Flatter recency curve to avoid too much recency bias
                recency_bonus = ((year - 1990) / (current_year - 1990)) * 0.1
                score += max(0, recency_bonus)
            except:
                pass
            
            return score

        sorted_results = sorted(unique_results, key=get_score, reverse=True)
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