from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
import os
from modules.suggestion import reccomend_movie
from modules.ai_suggestion import get_ai_suggestion
from modules.api import get_movie_details, get_tv_details, tmdb
from modules.stats import StatsTracker

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY')
app.config['DEBUG'] = True

stats_tracker = StatsTracker()

@app.route('/')
def index():
    return render_template('main.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/search', methods=['POST'])
def search():
    data = request.get_json()
    title = data.get('query')
    platform = data.get('category')
    
    # First get the actual searched movie/show from TMDb
    if platform == 'movie':
        search_results = tmdb.search().movies(query=title)
    else:
        search_results = tmdb.search().tv(query=title)
    
    # Get recommendations
    recommendations = reccomend_movie(title, platform)
    
    if recommendations:
        # Track the search using the actual searched title from TMDb
        if search_results and len(search_results) > 0:
            actual_title = search_results[0].name if platform == 'tv' else search_results[0].title
            stats_tracker.track_search(actual_title, platform)
        
        results = []
        for item in recommendations[:10]:
            result = {
                'id': item.id,
                'title': item.name if platform == 'tv' else item.title,
                'rating': item.vote_average,
                'popularity': item.popularity
            }
            results.append(result)
        return jsonify({'success': True, 'results': results})
    
    return jsonify({'success': False, 'message': 'No recommendations found'})

@app.route('/ai_suggest', methods=['POST'])
def ai_suggest():
    try:
        data = request.get_json()
        prompt = data.get('prompt')
        
        if not prompt:
            return jsonify({'success': False, 'message': 'No prompt provided'})
        
        suggestion = get_ai_suggestion(prompt)
        
        return jsonify({
            'success': True,
            'suggestion': suggestion
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        })

@app.route('/get_details', methods=['POST'])
def get_details():
    try:
        data = request.get_json()
        item_id = data.get('id')
        media_type = data.get('media_type')
        
        if not item_id or not media_type:
            return jsonify({'success': False, 'message': 'Missing id or media_type'})
        
        if media_type == 'movie':
            details = get_movie_details(tmdb, item_id)
        else:
            details = get_tv_details(tmdb, item_id)
            
        return jsonify({
            'success': True,
            'details': details
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        })
@app.route('/stats')
def stats():
    top_searches = stats_tracker.get_top_searches(limit=10)
    recent_searches = stats_tracker.get_recent_searches(limit=10)
    
    # Use a dictionary for total_stats
    total_stats = {
        'total_unique_titles': stats_tracker.get_total_unique_titles(),
        'total_searches': stats_tracker.get_total_searches(),
        'movie_titles': stats_tracker.get_movie_titles(),
        'tv_show_titles': stats_tracker.get_tv_show_titles()
    }
    
    return render_template('stats.html', 
                           top_searches=top_searches,
                           recent_searches=recent_searches,
                           total_stats=total_stats)
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)

