from flask import Flask, render_template, request, Response, jsonify
from prometheus_client import Counter, generate_latest
from src.core.planner import TravelPlanner
from dotenv import load_dotenv
import logging
import os

# Load environment variables
load_dotenv()

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Prometheus Metrics
REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total HTTP Requests",
    ["method", "endpoint", "status"]
)

# Global planner instance
travel_planner = None


def get_travel_planner():
    """
    Lazy load the TravelPlanner instance.
    Prevents startup crashes and optimizes resource usage.
    """
    global travel_planner

    if travel_planner is None:
        logger.info("Initializing TravelPlanner...")
        travel_planner = TravelPlanner()
        logger.info("TravelPlanner initialized successfully!")

    return travel_planner


def create_app():
    """
    Application factory function for Flask app creation.
    Enables easier testing and deployment.
    """
    app = Flask(__name__)
    app.template_folder = 'templates'
    app.static_folder = 'static'

    @app.route('/')
    def index():
        """Render the main page"""
        REQUEST_COUNT.labels(method='GET', endpoint='/', status=200).inc()
        logger.info("Index page requested")
        return render_template('index.html')

    @app.route('/health')
    def health():
        """Health check endpoint for monitoring"""
        REQUEST_COUNT.labels(method='GET', endpoint='/health', status=200).inc()
        logger.info("Health check requested")
        return jsonify({
            "status": "healthy",
            "service": "AI Travel Planner"
        }), 200

    @app.route('/generate-itinerary', methods=['POST'])
    def generate_itinerary():
        """Generate travel itinerary based on user input"""
        try:
            data = request.get_json()
            city = data.get('city', '').strip()
            interests = data.get('interests', '').strip()

            if not city or not interests:
                REQUEST_COUNT.labels(method='POST', endpoint='/generate-itinerary', status=400).inc()
                logger.warning("Invalid request: missing city or interests")
                return jsonify({
                    'success': False,
                    'error': 'Please fill in both City and Interests to proceed.'
                }), 400

            logger.info(f"Generating itinerary for city: {city}, interests: {interests}")

            # Get planner instance (lazy loaded)
            planner = get_travel_planner()
            planner.set_city(city)
            planner.set_interests(interests)
            itinerary = planner.create_itineary()

            REQUEST_COUNT.labels(method='POST', endpoint='/generate-itinerary', status=200).inc()
            logger.info("Itinerary generated successfully")

            return jsonify({
                'success': True,
                'itinerary': itinerary,
                'city': city,
                'interests': interests
            }), 200

        except Exception as e:
            REQUEST_COUNT.labels(method='POST', endpoint='/generate-itinerary', status=500).inc()
            logger.exception("Error generating itinerary")
            return jsonify({
                'success': False,
                'error': f'An error occurred: {str(e)}'
            }), 500

    @app.route('/about')
    def about():
        """Render the about page"""
        REQUEST_COUNT.labels(method='GET', endpoint='/about', status=200).inc()
        logger.info("About page requested")
        return render_template('about.html')

    @app.route('/metrics')
    def metrics():
        """Prometheus metrics endpoint"""
        REQUEST_COUNT.labels(method='GET', endpoint='/metrics', status=200).inc()
        logger.info("Metrics requested")
        return Response(
            generate_latest(),
            mimetype="text/plain"
        )

    return app


# Application instance
app = create_app()


# Local development
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("DEBUG", "True").lower() == "true"

    logger.info(f"Starting Flask app on port {port} with debug={debug}")
    print("\n" + "="*60)
    print(f"✅ Your AI Travel Agent is running!")
    print(f"🌐 Open your browser and go to:")
    print(f"   👉 http://localhost:{port}/")
    print("="*60 + "\n")

    app.run(
        host="0.0.0.0",
        port=port,
        debug=debug
    )