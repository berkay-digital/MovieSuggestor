if __name__ == "__main__":
    from api import get_id_by_title, get_popular_by_genre, get_movie_details, get_tv_details
    from api import tmdb
else:
    from modules.api import get_id_by_title, get_popular_by_genre, get_movie_details, get_tv_details
    from modules.api import tmdb


def reccomend_movie(title, platform):
    #Check if the user puts movie or tv
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
    elif tv_id:
        print("TV Show found")
        tv_details = get_tv_details(tmdb, tv_id)
        genres = tv_details
        media_type = 'tv'
    else:
        print("Movie or serie not found")
        return []
    
    #Reccomend movie/series based on genre
    recomendations = []
    for genre in genres:
        genre_recommendations = get_popular_by_genre(tmdb, genre, media_type=media_type)
        recomendations.extend(genre_recommendations)

    #Sorting based on the rating
    recomendations = sorted(recomendations, key=lambda x: x.vote_average, reverse=True)
    return recomendations

#Testing the function
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

