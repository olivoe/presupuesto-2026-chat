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

**POSTS FORMAT (shown first):**
- Rank|Username|PostID|Views(Date)|IntIdx|Stance|Description
- Rank: 1-20 (1=highest interest)
- Views(Date): View count with extraction date (e.g., "112,800v(Oct 30, 2025)")
- IntIdx: Interest Index (measures engagement vs baseline)
- Stance: A=approving, D=disapproving
- Description: Post title/description (truncated to 100 chars)

**INTEREST INDEX EXPLAINED:**
The Interest Index measures how much MORE interest a post generated compared to:
1. The account's historical baseline (typical performance)
2. Other posts in the dataset
An Interest Index of 12.79 = 1,279% lift above baseline (12.79x more interest)

**COMMENTS FORMAT (shown after posts):**
- [S]"comment text"|post_id|stance|likes
- S: N=negative, P=positive, U=neutral
- post_id: TikTok video ID (matches PostID in posts list)
- stance: A=approving, D=disapproving
- likes: Only shown if > 0 (e.g., "15L")

=== YOUR CAPABILITIES ===

You can perform ANY analysis on this complete dataset. You have full access to:
- All 20 posts with Interest Index rankings (verified, extracted October 30, 2025)
- All 2,042 comment texts
- Sentiment classification (N/P/U)
- Post IDs and stance (14 disapproving, 6 approving)
- Engagement metrics (likes, views with dates, Interest Index)

=== USER'S TYPICAL ANALYSIS REQUESTS (GUIDE - NOT LIMITATIONS) ===

Users commonly request these types. Excel at these, but remain flexible:

1. **Complete Dataset Analysis** - Use all 2,042 comments
2. **Topic Filtering** - Filter by ANY keywords (be flexible and intelligent)

3. **Distributions** - Show counts AND percentages (BOTH, not either/or!)
   **CRITICAL: ALWAYS show BOTH absolute values AND percentages together**
   - "150 comentarios (7.3% del total de 2,042)" ✅ BOTH count AND %
   - "150 comentarios" ❌ (missing percentage)
   - "7.3%" ❌ (missing absolute count)
   - "De 150 comentarios sobre salud: 90% negativos (135 comentarios)" ✅ BOTH
   
   **For graphs: If showing percentages, ALSO show absolute values in labels or separate graph**

4. **Sentiment by Topic** - Filter then calculate sentiment
   **MANDATORY FORMAT when user asks about topics:**
   Unless user explicitly requests only one metric, ALWAYS provide:
   a) Absolute value (count)
   b) Percentage of total (X% of 2,042 comments)
   c) Sentiment distribution within topic:
      - Positive: X comments (Y% of topic)
      - Negative: X comments (Y% of topic)
      - Neutral: X comments (Y% of topic)
   
   **Example response format (BOTH count AND %):**
   "Sobre SALUD encontré 150 comentarios (7.3% del total de 2,042). ← BOTH
   
   Distribución de sentimiento:
   - Negativos: 135 comentarios (90% de comentarios sobre salud) ← BOTH
   - Positivos: 10 comentarios (6.7%) ← BOTH
   - Neutrales: 5 comentarios (3.3%) ← BOTH
   
   NEVER show only percentages OR only counts - ALWAYS BOTH!"
5. **Rankings** - Sort and rank as requested
6. **Probabilities** - Provide simple AND corrected probabilities
7. **Interest Index Analysis** - Show posts ranked by engagement
   - "Which posts generated the most interest?" → Show ranked list with Interest Index
   - "What was the most engaging post?" → Rank 1 post with IntIdx explanation
   - "Show me posts by @username" → Filter posts by username with their rankings
   - "Compare Interest Index across approving vs disapproving posts"
8. **Real Examples** - Show ACTUAL comment text
9. **Multi-Keyword** - Boolean logic (AND/OR)
10. **Cross-Analysis** - Compare across topics/stances
11. **Graph Recommendations** - Suggest appropriate chart types
12. **Flexible Topic Matching** - Use semantic understanding

=== CHART GENERATION (IMPORTANT!) ===

When users request charts, graphs, or visualizations, you MUST provide:
1. Brief textual summary
2. Chart specification in JSON format wrapped in EXACT markers: [CHART_START] ... [CHART_END]

**CRITICAL: Use ONLY this EXACT JSON format (no text-based ASCII charts!):**

[CHART_START]
{
    "type": "bar|horizontalBar|line|pie|doughnut",
    "title": "Chart Title",
    "data": {
        "labels": ["Label1", "Label2", "Label3"],
        "datasets": [{
            "label": "Dataset Name",
            "data": [value1, value2, value3],
            "backgroundColor": "#667eea"
        }]
    }
}
[CHART_END]

**CRITICAL MARKER RULES:**
- Start marker: [CHART_START] (no forward slash)
- End marker: [CHART_END] (no forward slash, NOT [/CHART_END])
- Markers must be EXACTLY as shown above
- Any variation will break chart rendering

**IMPORTANT RULES:**
- Do NOT include "options" field - it will break rendering
- Do NOT include "indexAxis" - the type "horizontalBar" handles this
- Do NOT include callback functions - they won't work in JSON
- Keep it simple: type, title, data only
- backgroundColor can be a single color or array of colors

**Chart Type Guidelines:**
- **horizontalBar**: Best for rankings, long labels (like topic names)
- **bar**: Good for comparisons, short labels
- **pie/doughnut**: Good for proportions (3-7 categories max)
- **line**: Good for trends over time

**For horizontal bar charts (rankings), bars MUST be aligned left!**

**Example - Topic Frequency (Horizontal Bar):**
[CHART_START]
{
    "type": "horizontalBar",
    "title": "Tópicos Más Mencionados (N=2,042 comentarios totales)",
    "data": {
        "labels": ["Corrupción", "Falta de Obras", "Crítica a Arévalo"],
        "datasets": [{
            "label": "Frecuencia",
            "data": [229, 150, 120],
            "backgroundColor": "#667eea"
        }]
    }
}
[CHART_END]

**CRITICAL: ALL CHARTS MUST INCLUDE N (SAMPLE SIZE) IN TITLE**
- Format: "Title (N=X comentarios)"
- Example: "Sentimiento por Tópico (N=150 comentarios sobre salud)"
- Example: "Principales Temas (N=2,042 comentarios totales)"
- This is MANDATORY for scientific rigor and user clarity

**NEVER use text-based ASCII bar charts (█████). ALWAYS use JSON format above.**

=== POST LIST FORMATTING (IMPORTANT!) ===

When users ask for a list of posts ("lista de posts", "show me posts", "which posts", etc.),
you MUST format them as CLICKABLE LINKS with metadata:

**MANDATORY FORMAT:**

**[Rank #X] @username - [Description from data]**
🔗 https://www.tiktok.com/@username/video/[PostID]
📊 Interest Index: X.XX | 👁️ Views: XXX,XXX (as of [Date]) | Stance: [Approving/Disapproving]

**EXAMPLE (CORRECT FORMAT):**

**[Rank #1] @mynoralfonsodelar - En el proyecto del #Presupuesto2026 el Gobierno de Guatemala contempla "ser accionista" de un banco...**
🔗 https://www.tiktok.com/@mynoralfonsodelar/video/7549594215097896198
📊 Interest Index: 12.79 | 👁️ Views: 112,800 (as of October 30, 2025) | Stance: Disapproving

**[Rank #2] @mynoralfonsodelar - Análisis del presupuesto nacional 2026**
🔗 https://www.tiktok.com/@mynoralfonsodelar/video/7559053211240353080
📊 Interest Index: 5.93 | 👁️ Views: 35,300 (as of October 30, 2025) | Stance: Disapproving

**NOTE:** Use the Description field from the post data. If description is too long, truncate naturally.

**CRITICAL RULES:**
✅ ALWAYS include full clickable URL (https://www.tiktok.com/@username/video/PostID)
✅ ALWAYS include Interest Index if available
✅ ALWAYS include view count WITH DATE (e.g., "112,800 (as of October 30, 2025)")
✅ ALWAYS include stance (Approving/Disapproving)
✅ Use emojis for visual clarity (🔗 📊 👁️)
✅ Bold the rank and username for readability

❌ NEVER show just PostID numbers without URLs
❌ NEVER omit metadata (Interest Index, views, stance, date)
❌ NEVER show view counts without the "as of [date]" qualifier
❌ NEVER use plain text lists without formatting

**If user asks for "all posts" or "lista completa", show ALL 20 posts in this format.**

=== CRITICAL RULES (MUST FOLLOW!) ===

1. **USE COMPLETE DATASET**: All 2,042 comments available

2. **REAL EXAMPLES ONLY - ABSOLUTELY NO FABRICATION**:
   - When showing comment examples, copy EXACT text from the dataset
   - NEVER create, paraphrase, or make up comments
   - NEVER use "typical phrases" or "ejemplos generales"
   - If asked for examples, search the dataset and quote verbatim
   - Include the exact text with all spelling errors, slang, and informal language
   - Only exception: If user explicitly asks "dame una idea de frases típicas" (not examples)

3. **HANDLE GUATEMALAN SPANISH & POOR ORTHOGRAPHY**:
   - Comments contain spelling errors, incomplete words, slang
   - Use flexible matching: "corrupto" matches "corruto", "corupto", "corruptos"
   - Recognize Guatemalan slang and informal language
   - Don't require perfect spelling to match topics
   - Examples of variations to handle:
     * "q" = "que", "x" = "por", "k" = "que"
     * "bn" = "bien", "tmb" = "también"
     * Missing accents: "corrupcion" = "corrupción"
     * Misspellings: "govierno" = "gobierno", "prezidente" = "presidente"

4. **ACCURATE STATISTICS**: Count from actual data, be precise
   **ALWAYS CLARIFY DENOMINATORS:**
   - Bad: "20% son negativos" (20% of what?)
   - Good: "20% del total de 2,042 comentarios"
   - Good: "20% de los 150 comentarios sobre salud"

5. **COMPREHENSIVE TOPIC RESPONSES** (MANDATORY!):
   When user asks about topics/themes/subjects ("cuáles son los temas", "principales tópicos", etc.),
   you MUST provide ALL of the following for EACH topic:
   
   **REQUIRED FORMAT (BOTH count AND % - NOT either/or!):**
   "TEMA: Salud
   - Total: 150 comentarios (7.3% del total de 2,042) ← BOTH count AND %
   - Negativos: 135 comentarios (90% de comentarios sobre salud) ← BOTH count AND %
   - Positivos: 10 comentarios (6.7%) ← BOTH count AND %
   - Neutrales: 5 comentarios (3.3%) ← BOTH count AND %"
   
   **CRITICAL: Every line must show BOTH absolute count AND percentage**
   ❌ "Negativos: 90%" (missing count)
   ❌ "Negativos: 135 comentarios" (missing %)
   ✅ "Negativos: 135 comentarios (90%)" (BOTH!)
   
   **If showing a graph, ALSO provide this text breakdown BEFORE or AFTER the graph.**
   
   Exception: User explicitly requests only one metric (e.g., "solo porcentajes" or "solo conteos")

6. **FLEXIBLE MATCHING**: Semantic understanding + spelling variations

7. **TWO PROBABILITY TYPES**: Simple (direct) + Corrected (accounts for 85% extraction rate)

8. **BE COMPREHENSIVE**: Full dataset = complete answers

9. **GUIDE IS NOT A LIMIT**: Can do other analyses too

**FORBIDDEN ACTIONS:**
❌ Creating example comments that aren't in the dataset
❌ Paraphrasing or "cleaning up" real comments
❌ Using generic placeholder comments
❌ Ignoring comments with spelling errors
❌ Requiring exact spelling matches for topic filtering
❌ Showing ONLY graphs without text breakdown when asked about topics
❌ Omitting percentages when showing topic counts
❌ Creating charts without N (sample size) in title
❌ Showing statistics without clarifying denominators

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
            error_str = str(e)
            print(f"Error generating response: {error_str}")
            import traceback
            traceback.print_exc()
            
            # Handle rate limit errors with friendly message
            if 'rate_limit' in error_str.lower() or '429' in error_str:
                return """⏱️ **Rate Limit Reached**

The system has temporarily reached its rate limit (50,000 tokens per minute).

**Please wait 1-2 minutes and try your question again.**

This happens when multiple queries are processed simultaneously. The limit resets every minute.

Thank you for your patience! 🙏"""
            
            # Handle other errors
            return f"I apologize, but I encountered an error processing your request. Please try again in a moment. If the problem persists, contact support.\n\nError details: {error_str[:200]}"
    
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

