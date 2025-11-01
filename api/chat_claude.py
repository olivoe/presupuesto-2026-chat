"""
Chat API - Claude Haiku 3.5
Full dataset (44K tokens) with Claude's 50K TPM limit
"""

from http.server import BaseHTTPRequestHandler
import json
import os
from typing import List, Dict
from datetime import datetime
import anthropic

# Import full dataset loader
try:
    from .full_dataset_loader import get_full_dataset_loader
except ImportError:
    try:
        import sys
        sys.path.insert(0, os.path.dirname(__file__))
        from full_dataset_loader import get_full_dataset_loader
    except:
        get_full_dataset_loader = None

class handler(BaseHTTPRequestHandler):
    """Vercel serverless handler - Claude Haiku 3.5"""
    
    def do_POST(self):
        """Handle POST requests to /api/chat"""
        
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
            
            # Extract parameters
            message = data.get('message', '')
            conversation_history = data.get('conversation_history', [])
            session_id = data.get('session_id', 'default')
            
            if not message:
                response = {
                    'error': 'Message is required',
                    'response': '',
                    'sources': []
                }
                self.wfile.write(json.dumps(response).encode())
                return
            
            # Load full dataset
            full_context = ""
            if get_full_dataset_loader is not None:
                try:
                    loader = get_full_dataset_loader()
                    full_context = loader.create_compact_context()
                    print(f"✓ Loaded full dataset: {len(full_context)} chars")
                except Exception as e:
                    print(f"Error loading full dataset: {e}")
                    full_context = ""
            
            # Build prompt with full dataset
            system_prompt = self._build_system_prompt()
            user_prompt = self._build_user_prompt(message, full_context, conversation_history)
            
            # Generate response with Claude
            try:
                print(f"DEBUG: Generating response with Claude for: {message[:50]}...")
                answer = self._generate_response(system_prompt, user_prompt)
                print(f"DEBUG: Response generated, length: {len(answer)}")
            except Exception as gen_error:
                print(f"ERROR generating response: {str(gen_error)}")
                import traceback
                traceback.print_exc()
                answer = f"I apologize, but I encountered an error: {str(gen_error)}"
            
            # Log conversation
            try:
                self._log_conversation(
                    session_id=session_id,
                    user_message=message,
                    assistant_response=answer
                )
            except Exception as log_error:
                print(f"WARNING: Failed to log conversation: {log_error}")
            
            # Send response
            response = {
                'response': answer,
                'sources': [{'source': 'Complete Dataset (2,042 comments)', 'type': 'full_data'}],
                'session_id': session_id
            }
            
            self.wfile.write(json.dumps(response).encode())
            
        except Exception as e:
            print(f"ERROR in chat handler: {str(e)}")
            import traceback
            traceback.print_exc()
            
            error_response = {
                'error': str(e),
                'response': 'Sorry, there was an error processing your request.',
                'sources': []
            }
            self.wfile.write(json.dumps(error_response).encode())
    
    def do_OPTIONS(self):
        """Handle OPTIONS requests (CORS preflight)"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def _build_system_prompt(self) -> str:
        """Build system prompt for Claude"""
        
        return """You are an expert AI assistant specialized in the Presupuesto 2026 TikTok analysis project.

You have access to the COMPLETE DATASET of ALL 2,042 comments extracted from TikTok posts about Guatemala's 2026 budget.

The data is provided in ULTRA-COMPACT FORMAT:

**FORMAT:**
- [S]"comment text"|post_id|stance|likes
- S: N=negative, P=positive, U=neutral
- post_id: TikTok video ID
- stance: A=approving, D=disapproving
- likes: Only shown if > 0 (e.g., "15L")

=== YOUR CAPABILITIES ===

You can perform ANY analysis on this complete dataset. You have full access to:
- All 2,042 comment texts
- Sentiment classification (N/P/U)
- Post IDs and stance
- Engagement metrics (likes)

=== USER'S TYPICAL ANALYSIS REQUESTS (GUIDE - NOT LIMITATIONS) ===

Users commonly request these types. Excel at these, but remain flexible:

1. **Complete Dataset Analysis** - Use all 2,042 comments
2. **Topic Filtering** - Filter by ANY keywords (be flexible and intelligent)
3. **Distributions** - Show counts AND percentages
4. **Sentiment by Topic** - Filter then calculate sentiment
5. **Rankings** - Sort and rank as requested
6. **Probabilities** - Provide simple AND corrected probabilities
7. **Interest Index** - Connect comments to source posts
8. **Real Examples** - Show ACTUAL comment text
9. **Multi-Keyword** - Boolean logic (AND/OR)
10. **Cross-Analysis** - Compare across topics/stances
11. **Graph Recommendations** - Suggest appropriate chart types
12. **Flexible Topic Matching** - Use semantic understanding

=== CRITICAL RULES ===

1. **USE COMPLETE DATASET**: All 2,042 comments available
2. **REAL EXAMPLES ONLY**: Copy exact text, never fabricate
3. **ACCURATE STATISTICS**: Count from actual data
4. **FLEXIBLE MATCHING**: Semantic understanding, not just exact matches
5. **TWO PROBABILITY TYPES**: Simple (direct) + Corrected (accounts for 85% extraction rate)
6. **BE COMPREHENSIVE**: Full dataset = complete answers
7. **GUIDE IS NOT A LIMIT**: Can do other analyses too

=== RESPONSE STYLE ===

- Conversational but professional
- Same language as question (Spanish/English)
- Specific with numbers
- Show calculations when relevant
- Acknowledge extreme negativity (95.8%)
- Provide context and insights

Remember: You have COMPLETE access to ALL 2,042 comments. Use this to provide comprehensive, accurate analysis."""
    
    def _build_user_prompt(
        self,
        query: str,
        full_context: str,
        conversation_history: List[Dict[str, str]]
    ) -> str:
        """Build user prompt with dataset and history"""
        
        parts = []
        
        # Add full dataset
        if full_context:
            parts.append(full_context)
            parts.append("")
        
        # Add conversation history
        if conversation_history:
            parts.append("=== CONVERSATION HISTORY ===")
            for msg in conversation_history[-4:]:
                role = msg.get('role', 'user')
                content = msg.get('content', '')
                parts.append(f"{role.upper()}: {content}")
            parts.append("")
        
        # Add current query
        parts.append(f"USER QUERY: {query}")
        
        return "\n".join(parts)
    
    def _generate_response(self, system_prompt: str, user_prompt: str) -> str:
        """Generate response with Claude Haiku 3.5"""
        
        try:
            api_key = os.environ.get('ANTHROPIC_API_KEY')
            if not api_key:
                raise ValueError("ANTHROPIC_API_KEY environment variable is not set")
            
            client = anthropic.Anthropic(api_key=api_key)
            
            message = client.messages.create(
                model="claude-3-5-haiku-20241022",  # Claude Haiku 3.5
                max_tokens=2000,
                temperature=0.7,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": user_prompt}
                ]
            )
            
            return message.content[0].text
            
        except Exception as e:
            print(f"Error generating response: {e}")
            import traceback
            traceback.print_exc()
            return f"I apologize, but I encountered an error: {str(e)}"
    
    def _log_conversation(
        self,
        session_id: str,
        user_message: str,
        assistant_response: str
    ):
        """Log conversation to storage"""
        try:
            import tempfile
            from pathlib import Path
            
            log_entry = {
                'timestamp': datetime.utcnow().isoformat(),
                'session_id': session_id,
                'user_message': user_message,
                'assistant_response': assistant_response,
                'model': 'claude-3-5-haiku',
                'dataset_size': 2042
            }
            
            log_dir = Path('/tmp/chat_logs')
            log_dir.mkdir(exist_ok=True)
            
            log_file = log_dir / f"chat_log_{datetime.utcnow().strftime('%Y-%m-%d')}.jsonl"
            with open(log_file, 'a') as f:
                f.write(json.dumps(log_entry) + '\n')
            
            print(f"✓ Logged conversation: {session_id}")
            
        except Exception as e:
            print(f"Warning: Failed to log conversation: {e}")

