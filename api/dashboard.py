"""
Vercel Serverless Function for Admin Dashboard API
"""

from http.server import BaseHTTPRequestHandler
import json
import os
from typing import List, Dict, Any
from datetime import datetime, timedelta
from pathlib import Path
import hashlib

class handler(BaseHTTPRequestHandler):
    """Vercel serverless handler for dashboard"""
    
    def do_POST(self):
        """Handle POST requests to /api/dashboard"""
        
        # CORS headers
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        
        try:
            # Read request body
            content_length = int(self.headers['Content-Length'])
            body = self.rfile.read(content_length)
            data = json.loads(body.decode('utf-8'))
            
            action = data.get('action', '')
            password = data.get('password', '')
            
            # Authenticate
            if not self._authenticate(password):
                response = {
                    'error': 'Invalid password',
                    'authenticated': False
                }
                self.wfile.write(json.dumps(response).encode())
                return
            
            # Handle different actions
            if action == 'get_logs':
                days = data.get('days', 7)
                logs = self._get_logs(days)
                response = {
                    'authenticated': True,
                    'logs': logs,
                    'total': len(logs)
                }
            elif action == 'get_analytics':
                days = data.get('days', 7)
                analytics = self._get_analytics(days)
                response = {
                    'authenticated': True,
                    'analytics': analytics
                }
            elif action == 'export_logs':
                days = data.get('days', 30)
                logs = self._get_logs(days)
                response = {
                    'authenticated': True,
                    'logs': logs,
                    'export_format': 'json'
                }
            else:
                response = {
                    'error': 'Unknown action',
                    'authenticated': True
                }
            
            self.wfile.write(json.dumps(response).encode())
            
        except Exception as e:
            error_response = {
                'error': str(e),
                'authenticated': False
            }
            self.wfile.write(json.dumps(error_response).encode())
    
    def do_OPTIONS(self):
        """Handle OPTIONS requests (CORS preflight)"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def _authenticate(self, password: str) -> bool:
        """
        Authenticate dashboard access
        
        Password is stored as SHA256 hash in environment variable
        """
        # Get password hash from environment
        expected_hash = os.environ.get('DASHBOARD_PASSWORD_HASH', '')
        
        # If no hash set, use default (CHANGE THIS IN PRODUCTION!)
        if not expected_hash:
            # Default password: "hV+e?Wup+$RF^%MmjFR8Eh"
            expected_hash = "c398e8bcb5df3f3463ae375dec0831925c54b6943374513fc8d7b47c3cdf36d6"
        
        # Hash provided password
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        return password_hash == expected_hash
    
    def _get_logs(self, days: int = 7) -> List[Dict[str, Any]]:
        """
        Retrieve conversation logs from the last N days
        """
        try:
            log_dir = Path('/tmp/chat_logs')
            if not log_dir.exists():
                return []
            
            logs = []
            
            # Get logs from the last N days
            for i in range(days):
                date = datetime.utcnow() - timedelta(days=i)
                log_file = log_dir / f"chat_log_{date.strftime('%Y-%m-%d')}.jsonl"
                
                if log_file.exists():
                    with open(log_file, 'r') as f:
                        for line in f:
                            try:
                                log_entry = json.loads(line.strip())
                                logs.append(log_entry)
                            except:
                                continue
            
            # Sort by timestamp (newest first)
            logs.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
            
            return logs
            
        except Exception as e:
            print(f"Error retrieving logs: {e}")
            return []
    
    def _get_analytics(self, days: int = 7) -> Dict[str, Any]:
        """
        Generate analytics from conversation logs
        """
        try:
            logs = self._get_logs(days)
            
            if not logs:
                return {
                    'total_conversations': 0,
                    'total_messages': 0,
                    'unique_sessions': 0,
                    'avg_message_length': 0,
                    'avg_response_length': 0,
                    'queries_per_day': {},
                    'popular_topics': [],
                    'source_usage': {}
                }
            
            # Calculate metrics
            unique_sessions = set(log['session_id'] for log in logs)
            total_messages = len(logs)
            
            # Average lengths
            avg_msg_length = sum(log.get('message_length', 0) for log in logs) / total_messages
            avg_resp_length = sum(log.get('response_length', 0) for log in logs) / total_messages
            
            # Queries per day
            queries_per_day = {}
            for log in logs:
                date = log['timestamp'][:10]  # Extract YYYY-MM-DD
                queries_per_day[date] = queries_per_day.get(date, 0) + 1
            
            # Popular topics (extract keywords from user messages)
            topic_keywords = {}
            keywords = ['sentiment', 'interest', 'topic', 'post', 'comment', 'analysis', 
                       'chart', 'graph', 'visualization', 'recommendation', 'negative', 
                       'positive', 'corruption', 'budget', 'presupuesto']
            
            for log in logs:
                message = log.get('user_message', '').lower()
                for keyword in keywords:
                    if keyword in message:
                        topic_keywords[keyword] = topic_keywords.get(keyword, 0) + 1
            
            # Sort topics by frequency
            popular_topics = sorted(topic_keywords.items(), key=lambda x: x[1], reverse=True)[:10]
            
            # Source usage
            source_usage = {}
            for log in logs:
                for source in log.get('sources', []):
                    source_usage[source] = source_usage.get(source, 0) + 1
            
            return {
                'total_conversations': len(unique_sessions),
                'total_messages': total_messages,
                'unique_sessions': len(unique_sessions),
                'avg_message_length': round(avg_msg_length, 1),
                'avg_response_length': round(avg_resp_length, 1),
                'queries_per_day': queries_per_day,
                'popular_topics': popular_topics,
                'source_usage': source_usage,
                'date_range': {
                    'start': logs[-1]['timestamp'][:10] if logs else None,
                    'end': logs[0]['timestamp'][:10] if logs else None
                }
            }
            
        except Exception as e:
            print(f"Error generating analytics: {e}")
            return {}

