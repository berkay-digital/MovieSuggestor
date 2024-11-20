from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
import os
from modules.suggestion import reccomend_movie

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY')
app.config['DEBUG'] = True

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
    
    recommendations = reccomend_movie(title, platform)
    
    if recommendations:
        results = []
        for movie in recommendations[:5]:
            results.append({
                'title': movie.title,
                'rating': movie.vote_average,
                'popularity': movie.popularity
            })
        return jsonify({'success': True, 'results': results})
    
    return jsonify({'success': False, 'message': 'No recommendations found'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)

