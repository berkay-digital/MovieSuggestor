if __name__ == "__main__":
    from api import get_id_by_title, get_popular_by_genre, get_movie_details, get_tv_details
    from api import tmdb
else:
    from modules.api import get_id_by_title, get_popular_by_genre, get_movie_details, get_tv_details
    from modules.api import tmdb


GENRE_IDS = {
    'Action': 28,
    'Adventure': 12,
    'Animation': 16,
    'Comedy': 35,
    'Crime': 80,
    'Documentary': 99,
    'Drama': 18,
    'Family': 10751,
    'Fantasy': 14,
    'History': 36,
    'Horror': 27,
    'Music': 10402,
    'Mystery': 9648,
    'Romance': 10749,
    'Science Fiction': 878,
    'TV Movie': 10770,
    'Thriller': 53,
    'War': 10752,
    'Western': 37,
    # TV Show specific genres
    'Action & Adventure': 10759,
    'Kids': 10762,
    'News': 10763,
    'Reality': 10764,
    'Sci-Fi & Fantasy': 10765,
    'Soap': 10766,
    'Talk': 10767,
    'War & Politics': 10768
}


def get_genre_id(genre):
    if isinstance(genre, int):
        return genre
    return GENRE_IDS.get(genre)


def reccomend_movie(title, platform):
    movie_id = None
    tv_id = None

    if platform == 'movie':
        movie_id = get_id_by_title(tmdb, title, media_type='movie')
    elif platform == 'tv':
        tv_id = get_id_by_title(tmdb, title, media_type='tv')
    else:
        print("Invalid platform")
        return []

    if movie_id:
        print("Movie found")
        movie_details = get_movie_details(tmdb, movie_id)
        genres = movie_details['category']
        media_type = 'movie'

        genre_ids = []
        for genre in genres:
            genre_id = get_genre_id(genre)
            if genre_id:
                genre_ids.append(genre_id)
        genres = genre_ids

    elif tv_id:
        print("TV Show found")
        tv_details = get_tv_details(tmdb, tv_id)
        print(f"TV Details: {tv_details}")

        genres = []
        if 'category' in tv_details and tv_details['category']:
            for genre in tv_details['category']:
                genre_id = get_genre_id(genre)
                if genre_id:
                    genres.append(genre_id)

        print(f"Found genres: {genres}")
        media_type = 'tv'
    else:
        print("Movie or serie not found")
        return []

    if not genres:
        print("No genres found")
        return []

    recomendations = []
    for genre_id in genres:
        try:
            if media_type == 'tv':
                genre_recommendations = get_popular_by_genre(tmdb, genre_id, media_type=media_type)
            else:
                genre_recommendations = get_popular_by_genre(tmdb, genre_id, media_type=media_type, include_adult=False)

            if genre_recommendations:
                recomendations.extend(genre_recommendations)
        except Exception as e:
            print(f"Error getting popular {media_type} in genre {genre_id}: {str(e)}")
            continue

    recomendations = sorted(recomendations, key=lambda x: x.vote_average, reverse=True)
    return recomendations


# Testing the function
if __name__ == "__main__":
    title = input("Give the title of a movie or series: ")
    platform = input("Give the platform of the movie or series: ")
    recommendations = reccomend_movie(title, platform)

    if recommendations:
        print("Recomendations: ")
        for movie in recommendations[:5]:
            print(f"Title: {movie.title}, Rating: {movie.vote_average}, Popularity: {movie.popularity}")
    else:
        print("No reccomendations")

