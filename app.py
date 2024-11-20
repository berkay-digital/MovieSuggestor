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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)

