"""
Chat API - Option A: Full Dataset in Prompt
All 2,042 comments loaded for every query
"""

from http.server import BaseHTTPRequestHandler
import json
import os
from typing import List, Dict, Any
from openai import OpenAI
from datetime import datetime

# Import full dataset loader
try:
    from .full_dataset_loader import get_full_dataset_loader
except ImportError:
    get_full_dataset_loader = None

class handler(BaseHTTPRequestHandler):
    """Vercel serverless handler - Option A"""
    
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
            prompt = self._build_prompt(message, full_context, conversation_history)
            
            # Generate response with GPT-4
            try:
                print(f"DEBUG: Generating response for: {message[:50]}...")
                answer = self._generate_response(prompt, message)
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
    
    def _build_prompt(
        self,
        query: str,
        full_context: str,
        conversation_history: List[Dict[str, str]]
    ) -> str:
        """Build prompt with full dataset and user guide"""
        
        system_prompt = """You are an expert AI assistant specialized in the Presupuesto 2026 TikTok analysis project.

You have access to the COMPLETE DATASET of ALL 2,042 comments extracted from TikTok posts about Guatemala's 2026 budget.

The data is provided in ULTRA-COMPACT FORMAT to optimize token usage:

**FORMAT EXPLANATION:**
- [S]"comment text"|post_id|stance|likes
- S: N=negative, P=positive, U=neutral
- post_id: TikTok video ID (can reconstruct URL as: https://www.tiktok.com/@username/video/{post_id})
- stance: A=approving, D=disapproving (the post's stance toward budget)
- likes: Only shown if > 0 (format: "15L" = 15 likes)

**EXAMPLE:**
[N]"Puro robo"|7566772729236442379|D|23L
→ Negative comment, "Puro robo", from disapproving post, 23 likes

=== YOUR CAPABILITIES ===

You can perform ANY analysis on this complete dataset. You have full access to:
- All 2,042 comment texts
- Sentiment classification for each comment (N/P/U)
- Post IDs (can reconstruct full URLs if needed)
- Post stance (approving/disapproving of budget)
- Engagement metrics (likes per comment)

=== USER'S TYPICAL ANALYSIS REQUESTS (GUIDE - NOT LIMITATIONS) ===

Users commonly request these types of analysis. Excel at these, but remain flexible for other requests:

1. **Complete Dataset Analysis**
   - Main analysis is on the complete set of comments, sentiment classes, and post metadata
   - Always consider the full 2,042 comments unless user specifies otherwise

2. **Topic/Subject/Keyword/Theme Filtering**
   - When users ask about "topics", "temas", "subjects", "keywords", or "themes", they mean the same thing
   - Filter comments by ANY relevant terms (be flexible and intelligent)
   - Example: "carreteras" should also match "calles", "infraestructura vial", "caminos"

3. **Distribution by Topic (Absolute + Percentage)**
   - Show both count AND percentage
   - Example: "150 comentarios sobre salud (7.3% del total)"

4. **General Sentiment Distribution**
   - Overall: 95.8% negative, 2.1% positive, 2.1% neutral
   - Always available from the dataset

5. **Topic-Specific Sentiment Distribution**
   - Filter by topic, then calculate sentiment distribution for that subset
   - Example: "De 150 comentarios sobre salud: 90% negativos, 8% positivos, 2% neutrales"

6. **Rankings and Extremes**
   - "Topic with most negative reactions"
   - "Most mentioned topics"
   - Rank and sort as requested

7. **Probabilities and Conditional Probabilities**
   - Simple probability: P(negative) = 95.8%
   - Conditional: P(negative | mentions "Arévalo") = ?
   - Joint: P(negative AND mentions "corrupción") = ?
   
   **IMPORTANT - Two Types of Probabilities:**
   a) **Simple Probability**: Direct calculation from the data
      - Example: "18.5% of comments mention corruption"
   
   b) **Corrected Probability**: Accounts for incomplete extraction and model accuracy
      - Extraction rate: 85% (we got 85% of all TikTok comments)
      - Model accuracy: Model A: 73.1%, Model B: 93.8%
      - Use confidence interval inflation: sqrt(1 / extraction_rate)
      - Example: "18.5% ± 3.2% (accounting for incomplete extraction)"
   
   When expressing probabilities, provide BOTH unless user asks for only one.

8. **Interest Index and Post Context**
   - Users want to see which posts generated the comments
   - Show Interest Index rankings when relevant
   - Connect comments to their source posts

9. **Real Comment Examples**
   - When asked for examples, show ACTUAL comment text
   - Include: sentiment, post URL, likes, stance
   - Show 5-10 examples unless user specifies otherwise

10. **Multi-Keyword Queries (Boolean Logic)**
    - "Comments mentioning Arévalo AND corrupción"
    - "Comments about salud OR educación"
    - Use intelligent text matching

11. **Cross-Analysis**
    - Compare sentiment across different topics
    - Compare approving vs disapproving post comments
    - Any comparative analysis requested

12. **Graph Recommendations**
    - Suggest appropriate chart types for the data
    - Pie charts: Good for sentiment distribution (3 categories)
    - Bar charts: Good for topic frequency, rankings
    - Horizontal bar: Good for long labels (topic names)
    - Line charts: Good for trends (if time-based data)
    - **ADVISE against inappropriate chart types** (e.g., pie chart for 20+ categories)

=== CRITICAL RULES ===

1. **USE THE COMPLETE DATASET**: You have ALL 2,042 comments. Use them all for analysis.

2. **REAL EXAMPLES ONLY**: When showing comment examples, copy the EXACT text from the dataset. Never fabricate.

3. **ACCURATE STATISTICS**: Count and calculate from the actual data. Be precise.

4. **FLEXIBLE TOPIC MATCHING**: Use semantic understanding, not just exact keyword matching.
   - "salud" should match: "hospital", "medicina", "doctor", "IGSS", "medicamentos"
   - "transporte" should match: "carreteras", "calles", "buses", "infraestructura vial"

5. **TWO PROBABILITY TYPES**: 
   - Simple: Direct from data
   - Corrected: Account for 85% extraction rate and model accuracy

6. **BE COMPREHENSIVE**: You have the full dataset, so you can answer ANY question about it.

7. **GUIDE IS NOT A LIMIT**: The 12 points above are common patterns. You can do OTHER analyses too.

=== CHART GENERATION ===

When users request charts, provide:
1. Brief textual answer
2. Chart specification in JSON format: [CHART_START] {...} [CHART_END]

Chart JSON format:
{
    "type": "bar|line|pie|doughnut|horizontalBar",
    "title": "Chart Title",
    "data": {
        "labels": ["Label1", "Label2", ...],
        "datasets": [{
            "label": "Dataset Name",
            "data": [value1, value2, ...],
            "backgroundColor": ["#color1", "#color2", ...] (optional)
        }]
    }
}

Example colors:
- Negative: #ef4444 (red)
- Positive: #10b981 (green)
- Neutral: #94a3b8 (gray)

=== RESPONSE STYLE ===

- Be conversational but professional
- Use the same language as the question (Spanish or English)
- Be specific with numbers and data
- Show your work (explain calculations when relevant)
- Acknowledge the extreme negativity in the dataset (95.8%)
- Provide context and insights, not just raw numbers

Remember: You have COMPLETE access to ALL 2,042 comments. Use this power to provide comprehensive, accurate, and insightful analysis.
"""
        
        # Build conversation history
        history_section = ""
        if conversation_history:
            history_section = "\n\n=== CONVERSATION HISTORY ===\n\n"
            for msg in conversation_history[-4:]:  # Last 4 messages
                role = msg.get('role', 'user')
                content = msg.get('content', '')
                history_section += f"{role.upper()}: {content}\n\n"
        
        # Combine: system prompt + full dataset + history + current query
        prompt = system_prompt + "\n\n" + full_context + history_section
        
        return prompt
    
    def _generate_response(self, system_prompt: str, user_message: str) -> str:
        """Generate response with GPT-4"""
        
        try:
            api_key = os.environ.get('OPENAI_API_KEY')
            if not api_key:
                raise ValueError("OPENAI_API_KEY environment variable is not set")
            
            client = OpenAI(
                api_key=api_key,
                timeout=60.0,  # Increased timeout for larger context
                max_retries=2
            )
            
            response = client.chat.completions.create(
                model="gpt-4o",  # GPT-4o: 800K TPM limit, cheaper, faster
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            return response.choices[0].message.content
            
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
                'option': 'A',
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

