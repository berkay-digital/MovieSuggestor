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

    unique_recommendations = {}
    
    if movie_id:
        print("Movie found")
        movie_details = get_movie_details(tmdb, movie_id)
        genres = movie_details['category']
        media_type = 'movie'

        # Get similar movies
        try:
            similar_movies = tmdb.movie(movie_id).similar()
            print(f"\nSimilar movies found: {len(similar_movies.results)}")
            
            # Sort similar movies by popularity
            sorted_similar = sorted(similar_movies.results, key=lambda x: x.popularity, reverse=True)
            
            for item in sorted_similar[:5]:
                if item.id != movie_id:
                    print(f"Similar movie: {item.title} (ID: {item.id}, Popularity: {item.popularity})")
                    unique_recommendations[item.id] = {
                        'item': item,
                        'matching_genres': 2,
                        'score': calculate_recommendation_score(item, 2)
                    }
        except Exception as e:
            print(f"Error getting similar movies: {str(e)}")

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

        # Get similar TV shows
        try:
            similar_shows = tmdb.tv(tv_id).similar()
            print(f"\nSimilar TV shows found: {len(similar_shows.results)}")
            
            # Sort similar shows by popularity
            sorted_similar = sorted(similar_shows.results, key=lambda x: x.popularity, reverse=True)
            
            for item in sorted_similar[:5]:
                if item.id != tv_id:
                    print(f"Similar TV show: {item.name} (ID: {item.id}, Popularity: {item.popularity})")
                    unique_recommendations[item.id] = {
                        'item': item,
                        'matching_genres': 2,
                        'score': calculate_recommendation_score(item, 2)
                    }
        except Exception as e:
            print(f"Error getting similar TV shows: {str(e)}")

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

    # Calculate how many more recommendations we need
    remaining_slots = 10 - len(unique_recommendations)
    recommendations_per_genre = max(2, remaining_slots // len(genres))
    
    # Get recommendations for individual genres
    for genre_id in genres:
        try:
            genre_recommendations = get_popular_by_genre(tmdb, genre_id, media_type=media_type, include_adult=False)
            if genre_recommendations:
                added_from_genre = 0
                for item in genre_recommendations:
                    if added_from_genre >= recommendations_per_genre:
                        break
                        
                    if item.id not in unique_recommendations and \
                       ((media_type == 'movie' and item.id != movie_id) or \
                        (media_type == 'tv' and item.id != tv_id)):
                        unique_recommendations[item.id] = {
                            'item': item,
                            'matching_genres': 1,
                            'score': calculate_recommendation_score(item, 1)
                        }
                        added_from_genre += 1

        except Exception as e:
            print(f"Error getting popular {media_type} in genre {genre_id}: {str(e)}")
            continue

    # Sort recommendations by score
    sorted_recommendations = sorted(
        unique_recommendations.values(),
        key=lambda x: x['score'],
        reverse=True
    )

    print(f"\nTotal recommendations found: {len(sorted_recommendations)}")
    
    # Separate similar and genre-based recommendations
    similar_recs = []
    genre_recs = []
    
    for rec in sorted_recommendations:
        if rec['matching_genres'] == 2:  # Similar content has matching_genres = 2
            similar_recs.append(rec['item'])
        else:
            genre_recs.append(rec['item'])
    
    # Get top 5 from each category
    similar_recs = similar_recs[:5]
    genre_recs = genre_recs[:5]
    
    # If we don't have enough recommendations in either category, fill from the other
    while len(similar_recs) + len(genre_recs) < 10:
        if len(similar_recs) < 5 and len(genre_recs) > 5:
            similar_recs.append(genre_recs.pop(5))
        elif len(genre_recs) < 5 and len(similar_recs) > 5:
            genre_recs.append(similar_recs.pop(5))
        else:
            # If we still need more recommendations, get them from popular
            try:
                if media_type == 'movie':
                    popular = tmdb.movies().popular()
                else:
                    popular = tmdb.tv().popular()
                
                existing_ids = [r.id for r in similar_recs + genre_recs]
                for item in popular.results:
                    if len(similar_recs) + len(genre_recs) >= 10:
                        break
                    if item.id not in existing_ids:
                        if len(similar_recs) < 5:
                            similar_recs.append(item)
                        else:
                            genre_recs.append(item)
            except Exception as e:
                print(f"Error getting popular {media_type}: {str(e)}")
            break

    # Mix the recommendations
    final_recommendations = []
    for i in range(max(len(similar_recs), len(genre_recs))):
        if i < len(similar_recs):
            final_recommendations.append(similar_recs[i])
        if i < len(genre_recs):
            final_recommendations.append(genre_recs[i])
            
    return final_recommendations[:10]

def calculate_recommendation_score(item, matching_genres):
    # Base score from rating (0-10)
    rating_score = item.vote_average * 0.4

    # Popularity score (normalized to 0-1 range)
    popularity_score = min(item.popularity / 1000, 1) * 0.2

    # Vote count score (normalized to 0-1 range)
    vote_count_score = min(item.vote_count / 10000, 1) * 0.1

    # Genre matching bonus (0.15 per matching genre)
    genre_score = matching_genres * 0.15

    # Calculate recency score based on release date
    try:
        release_year = int(item.release_date[:4] if hasattr(item, 'release_date') else 
                          item.first_air_date[:4] if hasattr(item, 'first_air_date') else 
                          2000)
        current_year = 2024
        recency_score = ((release_year - 2000) / (current_year - 2000)) * 0.15
        recency_score = max(0, min(recency_score, 0.15))
    except:
        recency_score = 0

    # Combine all scores
    total_score = rating_score + popularity_score + vote_count_score + genre_score + recency_score

    return total_score


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

