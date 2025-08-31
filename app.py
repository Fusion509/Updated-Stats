from flask import Flask, render_template, jsonify, request
import subprocess
import sys
import os
import json
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Add scrapers to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'Total PPO'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'Total Internship Offers'))

# Global variables to store results
ppo_results = {}
internship_results = {}
last_updated = None

def run_ppo_scraper():
    """Run PPO scraper and return results"""
    try:
        import importlib.util
        ppo_path = os.path.join(os.path.dirname(__file__), 'Total PPO', 'scrapper.py')
        spec = importlib.util.spec_from_file_location("ppo_scrapper", ppo_path)
        ppo_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(ppo_module)
        
        results, totals = ppo_module.scrape_ppos()
        return {
            'success': True,
            'results': results,
            'totals': totals,
            'timestamp': datetime.now().isoformat()
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }

def run_internship_scraper():
    """Run internship scraper and return results"""
    try:
        import importlib.util
        internship_path = os.path.join(os.path.dirname(__file__), 'Total Internship Offers', 'scrapper.py')
        spec = importlib.util.spec_from_file_location("internship_scrapper", internship_path)
        internship_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(internship_module)
        
        results, totals = internship_module.scrape_offers()
        return {
            'success': True,
            'results': results,
            'totals': totals,
            'timestamp': datetime.now().isoformat()
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/run-scrapers', methods=['POST'])
def run_scrapers():
    """Run both scrapers and return results"""
    global ppo_results, internship_results, last_updated
    
    try:
        # Run PPO scraper
        ppo_data = run_ppo_scraper()
        if ppo_data['success']:
            ppo_results = ppo_data['results']
            ppo_totals = ppo_data['totals']
        else:
            return jsonify({'success': False, 'error': f'PPO scraper failed: {ppo_data["error"]}'})
        
        # Run internship scraper
        internship_data = run_internship_scraper()
        if internship_data['success']:
            internship_results = internship_data['results']
            internship_totals = internship_data['totals']
        else:
            return jsonify({'success': False, 'error': f'Internship scraper failed: {internship_data["error"]}'})
        
        last_updated = datetime.now()
        
        # Combine results
        combined_results = {
            'success': True,
            'ppos': {
                'results': ppo_results,
                'totals': ppo_totals
            },
            'internships': {
                'results': internship_results,
                'totals': internship_totals
            },
            'timestamp': last_updated.isoformat(),
            'summary': {
                'total_ppos': ppo_totals.get('selected', 0),  # Only selected PPOs
                'total_internships': internship_totals.get('selected', 0),  # Only selected internships
                'grand_total': ppo_totals.get('selected', 0) + internship_totals.get('selected', 0)  # Total selected offers only
            }
        }
        
        return jsonify(combined_results)
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/get-results')
def get_results():
    """Get current results without running scrapers"""
    if not ppo_results and not internship_results:
        return jsonify({'success': False, 'message': 'No results available. Run scrapers first.'})
    
    return jsonify({
        'success': True,
        'ppos': ppo_results,
        'internships': internship_results,
        'last_updated': last_updated.isoformat() if last_updated else None
    })

if __name__ == '__main__':
    debug_mode = os.getenv('FLASK_DEBUG', 'false').lower() == 'true'
    app.run(debug=debug_mode, host='0.0.0.0', port=int(os.getenv('PORT', 5000)))
