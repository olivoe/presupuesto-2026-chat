"""
Simple test endpoint
"""

from http.server import BaseHTTPRequestHandler
import json
import os

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        # Test if env var exists
        api_key = os.environ.get('OPENAI_API_KEY')
        has_key = api_key is not None and len(api_key) > 0
        
        response = {
            'status': 'ok',
            'has_openai_key': has_key,
            'key_length': len(api_key) if api_key else 0
        }
        
        self.wfile.write(json.dumps(response).encode())

