from flask import Flask, render_template, request, jsonify
from src.core.planner import TravelPlanner
from dotenv import load_dotenv
import os

app = Flask(__name__)
app.template_folder = 'templates'
app.static_folder = 'static'

load_dotenv()

@app.route('/')
def index():
    """Render the main page"""
    return render_template('index.html')

@app.route('/generate-itinerary', methods=['POST'])
def generate_itinerary():
    """Generate travel itinerary based on user input"""
    try:
        data = request.get_json()
        city = data.get('city', '').strip()
        interests = data.get('interests', '').strip()
        
        if not city or not interests:
            return jsonify({
                'success': False,
                'error': 'Please fill in both City and Interests to proceed.'
            }), 400
        
        # Initialize planner and generate itinerary
        planner = TravelPlanner()
        planner.set_city(city)
        planner.set_interests(interests)
        itinerary = planner.create_itineary()
        
        return jsonify({
            'success': True,
            'itinerary': itinerary,
            'city': city,
            'interests': interests
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'An error occurred: {str(e)}'
        }), 500

@app.route('/about')
def about():
    """Render the about page"""
    return render_template('about.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)