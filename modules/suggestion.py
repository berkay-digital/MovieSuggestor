from api import get_id_by_title, get_popular_by_genre, get_movie_details, get_tv_details
from api import tmdb


def reccomend_movie(title):
    #Check if the user puts movie or tv
    movie_id = get_id_by_title(tmdb, title, media_type='movie')
    tv_id = get_id_by_title(tmdb, title, media_type='tv')

    if movie_id:
        movie_details = get_movie_details(tmdb, movie_id)
        genres = movie_details['category']
        media_type = 'movie'
    elif tv_id:
        tv_details = get_tv_details(tmdb, tv_id)
        genres = tv_details
        media_type = 'tv'
    else:
        print("Movie or serie not found")
        return []

