"""
Vercel Serverless Function for Chat API
"""

from http.server import BaseHTTPRequestHandler
import json
import os
from typing import List, Dict, Any
from openai import OpenAI
from datetime import datetime
import hashlib

# Import memory system with try/except for robustness
try:
    from .memory import MemorySystem
except ImportError:
    # Fallback if import fails
    MemorySystem = None

class handler(BaseHTTPRequestHandler):
    """Vercel serverless handler"""
    
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
            
            # Initialize memory system (if available)
            memory_context = ""
            if MemorySystem is not None:
                try:
                    memory = MemorySystem()
                    memory_context = memory.get_memory_context(message)
                except Exception as e:
                    print(f"Memory system error: {e}")
                    memory_context = ""
            
            # Retrieve relevant context (using pre-built knowledge base)
            contexts = self._retrieve_context(message, top_k=8)
            
            # Build prompt
            prompt = self._build_prompt(message, contexts, conversation_history, memory_context)
            
            # Generate response with GPT-4
            answer = self._generate_response(prompt, message)
            
            # Extract sources
            sources = [
                {
                    'source': ctx['metadata'].get('source', 'Unknown'),
                    'type': ctx['metadata'].get('type', 'Unknown')
                }
                for ctx in contexts
            ]
            
            # Log conversation
            self._log_conversation(
                session_id=session_id,
                user_message=message,
                assistant_response=answer,
                sources=sources
            )
            
            # Send response
            response = {
                'response': answer,
                'sources': sources,
                'session_id': session_id
            }
            
            self.wfile.write(json.dumps(response).encode())
            
        except Exception as e:
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
    
    def _retrieve_context(self, query: str, top_k: int = 8) -> List[Dict[str, Any]]:
        """
        Retrieve relevant context from knowledge base
        
        Enhanced KB with:
        - Precise statistics and bias-corrected sentiment data
        - Interest Index rankings and methodology
        - Account-specific performance data
        - FAQs for common questions
        - Topic analysis with psychosocial insights
        - Strategic recommendations
        """
        
        # Load pre-computed knowledge base summaries from environment or file
        # For now, return static high-level context
        
        contexts = [
            {
                'text': """Presupuesto 2026 Analysis Overview:
                - Total Posts Analyzed: 24 TikTok posts (21 with comments extracted)
                - Total Comments: 2,042 comments analyzed
                - Post Distribution: 7 approving posts (383 comments), 14 disapproving posts (1,659 comments)
                - Comment Extraction Rate: 85% (estimated)
                - Analysis Period: Posts from October-November 2025
                - Sentiment Analysis: Dual model approach (Model A for approving posts: 73.1% accuracy, Model B for disapproving posts: 93.8% accuracy)
                - Training Data: 172 manually annotated comments
                - Interest Index: Calculated using historical baseline (account performance) and relative baseline (peer comparison)
                - Top Interest Index: 12.799 (@mynoralfonsodelar - 112,800 views, 1,179.9% lift)
                """,
                'metadata': {'source': 'Project Overview', 'type': 'summary'}
            },
            {
                'text': """Sentiment Analysis Findings (Bias-Corrected):
                OVERALL SENTIMENT (2,042 comments):
                - Negative: 95.8% (CI: 81.5%-98.9%)
                - Positive: 2.1% (CI: 0%-13.8%)
                - Neutral: 2.1% (CI: 0.9%-6.4%)
                
                APPROVING POSTS (383 comments):
                - Negative: 85.4% (CI: 81.5%-89.2%)
                - Positive: 10.4% (CI: 7.1%-13.8%)
                - Neutral: 4.2% (CI: 2.0%-6.4%)
                
                DISAPPROVING POSTS (1,659 comments):
                - Negative: 98.3% (CI: 97.6%-98.9%)
                - Positive: 0.2% (CI: 0%-0.4%)
                - Neutral: 1.6% (CI: 0.9%-2.2%)
                
                METHODOLOGY:
                - Dual ML models: Model A (approving): 73.1% accuracy, Model B (disapproving): 93.8% accuracy
                - Training: 172 manually annotated comments
                - Bias correction: Missing Data CI Inflation (extraction rate: 85%)
                - Weighted by likes: Negative comments receive significantly more engagement
                """,
                'metadata': {'source': 'Sentiment Analysis', 'type': 'analysis'}
            },
            {
                'text': """Top 10 Topics (by frequency):
                1. Corrupción (229 mentions) - Dispositional attribution, institutional distrust
                2. Presidente Arévalo (159 mentions) - Personalization, confirmation bias
                3. Congreso/Diputados (121 mentions) - Elite capture narrative
                4. Presupuesto 2026 (84 mentions) - Trigger for accumulated grievances
                5. Infraestructura vial (61 mentions) - Tangible proof of state failure
                6. Sueldos/privilegios (49 mentions) - Distributive injustice
                7. Partidos políticos (40 mentions) - Identity polarization
                8. Impuestos/SAT (33 mentions) - Fiscal delegitimization
                9. Pobreza/costo de vida (32 mentions) - Economic stress
                10. Ministros/Gabinete (29 mentions) - Reputation contagion
                """,
                'metadata': {'source': 'Topic Analysis', 'type': 'topics'}
            },
            {
                'text': """Psychosocial Insights:
                - Extreme affective polarization dominates discourse
                - Moralization: Budget framed as moral offense (corruption, injustice)
                - Personalization: Blame concentrated on visible actors (President, Congress)
                - Tangible evidence: Road conditions, healthcare failures validate negative narratives
                - Fiscal erosion: Tax payment seen as unfair when state appears captured
                - Identity anchors: Partisan labels intensify hostile attribution
                """,
                'metadata': {'source': 'Psychosocial Analysis', 'type': 'insights'}
            },
            {
                'text': """Strategic Communication Recommendations:
                WHAT WORKS:
                - Concrete evidence (completed projects, delivered medicines)
                - Verifiable timelines and milestones
                - Transparency mechanisms (open audits, public milestones)
                - Micro-evidences of change
                
                WHAT DOESN'T WORK:
                - Technical explanations without accountability guarantees
                - General promises without evidence
                - Ignoring moral grievances
                
                KEYS TO TRUST:
                - Acknowledge accumulated frustrations
                - Use distributive justice language
                - Show tangible results
                - Establish credible monitoring systems
                """,
                'metadata': {'source': 'Strategic Recommendations', 'type': 'recommendations'}
            },
            {
                'text': """Interest Index Rankings (Top 10 Posts):
                1. @mynoralfonsodelar (disapproving): Interest Index 12.80, 112,800 views, 1,179.9% lift
                2. @mynoralfonsodelar (disapproving): Interest Index 5.93, 35,300 views, 492.8% lift
                3. @defensapropiedadprivada (disapproving): Interest Index 3.83, 16,100 views, 282.9% lift
                4. @dougcrisgt (disapproving): Interest Index 3.32, 189,400 views, 232.4% lift
                5. @chechinrodas (approving): Interest Index 2.76, 2,481 views, 176.2% lift
                6. @congreso.guate (approving): Interest Index 2.65, 18,900 views, 164.9% lift
                7. @mynoralfonsodelar (disapproving): Interest Index 2.62, 13,600 views, 161.6% lift
                8. @congreso.guate (approving): Interest Index 2.45, 3,186 views, 144.6% lift
                9. @zonanoticiasguatemala (disapproving): Interest Index 2.06, 3,331 views, 106.0% lift
                10. @bancada_cabal (disapproving): Interest Index 1.97, 1,932 views, 97.4% lift
                
                KEY INSIGHT: Disapproving posts dominate the top rankings (7 out of 10), with @mynoralfonsodelar showing exceptional performance.
                """,
                'metadata': {'source': 'Interest Index Rankings', 'type': 'data'}
            },
            {
                'text': """Interest Index Methodology:
                WHAT IS INTEREST INDEX?
                - Measures how much a video exceeded expected performance (baseline)
                - Interest Index = 1.0 means performance equal to baseline (0% lift)
                - Interest Index = 2.0 means 2× baseline (100% lift)
                - Interest Index = 12.8 means 12.8× baseline (1,180% lift)
                
                CALCULATION:
                - Combines Historical Lift (vs account's typical performance) and Relative Lift (vs other posts in dataset)
                - Uses geometric mean of normalized views, likes, comments, and shares
                - Time-normalized to account for post age
                - Bootstrap confidence intervals for uncertainty quantification
                
                FORMULA FOR LIFT:
                Lift % = (Interest Index - 1) × 100
                
                EXAMPLE:
                Interest Index of 12.799 = 1,179.9% more views than expected, or 1,279.9% of baseline
                """,
                'metadata': {'source': 'Interest Index Methodology', 'type': 'methodology'}
            },
            {
                'text': """Key Accounts and Their Performance:
                @mynoralfonsodelar (disapproving):
                - 3 posts analyzed
                - Top Interest Index: 12.80 (112,800 views)
                - Consistently high engagement
                - Focus: Critical of budget and government
                
                @congreso.guate (approving):
                - 2 posts analyzed
                - Interest Index: 2.65 and 2.45
                - Official Congress account
                - Focus: Defending budget decisions
                
                @defensapropiedadprivada (disapproving):
                - Interest Index: 3.83 (16,100 views)
                - High engagement rate: 11.0%
                - Focus: Property rights and government criticism
                
                @dougcrisgt (disapproving):
                - Interest Index: 3.32 (189,400 views)
                - Highest raw view count in dataset
                - Focus: Political commentary
                
                @bancada_cabal (stance changed from approving to disapproving):
                - Originally labeled approving, corrected to disapproving
                - Shows complexity of political positioning
                """,
                'metadata': {'source': 'Account Analysis', 'type': 'data'}
            },
            {
                'text': """Frequently Asked Questions (FAQs):
                
                Q: How many posts were analyzed?
                A: 24 TikTok posts total, with 21 posts having comments extracted (2,042 total comments).
                
                Q: What is the Interest Index?
                A: A metric showing how much a video exceeded expected performance. Index of 1.0 = baseline, 2.0 = 100% lift, 12.8 = 1,180% lift.
                
                Q: What does "lift" mean?
                A: Lift is the percentage increase above baseline. Calculated as: (Interest Index - 1) × 100.
                
                Q: Why are there two sentiment models?
                A: Approving and disapproving posts have different linguistic contexts. Separate models (Model A and Model B) improve accuracy.
                
                Q: What is bias correction?
                A: We only extracted 85% of comments. Missing Data CI Inflation widens confidence intervals to account for uncertainty from incomplete data.
                
                Q: What are the main topics?
                A: Top 3: Corrupción (229 mentions), Presidente Arévalo (159), Congreso/Diputados (121).
                
                Q: What's the overall sentiment?
                A: Extremely negative: 95.8% negative, 2.1% positive, 2.1% neutral (bias-corrected).
                
                Q: Which post performed best?
                A: @mynoralfonsodelar with Interest Index 12.80 (112,800 views, 1,179.9% lift above baseline).
                """,
                'metadata': {'source': 'FAQs', 'type': 'reference'}
            }
        ]
        
        return contexts[:top_k]
    
    def _build_prompt(
        self,
        query: str,
        contexts: List[Dict[str, Any]],
        conversation_history: List[Dict[str, str]],
        memory_context: str = ""
    ) -> str:
        """Build prompt for LLM with memory context"""
        
        system_prompt = """You are an expert AI assistant specialized in the Presupuesto 2026 TikTok analysis project.

Your role is to answer questions about:
- TikTok posts related to "Presupuesto 2026" (Guatemala's 2026 budget)
- Interest Index analysis and post rankings
- Comment sentiment analysis (positive, negative, neutral)
- Weighted sentiment analysis (considering comment likes)
- Topic analysis and psychosocial insights
- Strategic communication recommendations

Guidelines:
1. Answer based on the provided context
2. Be specific with numbers and data when available
3. If unsure, say so clearly
4. Be conversational but professional
5. The analysis shows EXTREME negativity (1,957 negative vs 43 positive vs 42 neutral)
6. Highlight psychosocial insights when relevant
7. Use relevant past Q&As from memory to provide consistent, accurate answers
8. Reference previous explanations when appropriate

CHART GENERATION CAPABILITY:
When the user asks for a chart, graph, visualization, or visual representation, you should:
1. Provide a brief textual answer
2. Include a chart specification in JSON format wrapped in special markers: [CHART_START] ... [CHART_END]

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
    },
    "options": {
        "description": "Brief description of what the chart shows"
    }
}

Example chart types you can generate:
- Sentiment distribution (pie/doughnut chart)
- Top topics by frequency (bar chart)
- Interest Index rankings (horizontal bar chart)
- Sentiment comparison across posts (bar chart)
- Time-based trends (line chart)

Answer in the same language as the question (English or Spanish).
"""
        
        # Build context section
        context_section = "\n\n=== RELEVANT CONTEXT ===\n\n"
        for i, ctx in enumerate(contexts, 1):
            context_section += f"[Context {i}]:\n{ctx['text']}\n\n"
        
        # Add memory context if available
        memory_section = ""
        if memory_context:
            memory_section = memory_context
        
        # Build conversation history
        history_section = ""
        if conversation_history:
            history_section = "\n\n=== CONVERSATION HISTORY ===\n\n"
            for msg in conversation_history[-4:]:  # Last 4 messages
                role = msg.get('role', 'user')
                content = msg.get('content', '')
                history_section += f"{role.upper()}: {content}\n\n"
        
        prompt = system_prompt + context_section + memory_section + history_section
        
        return prompt
    
    def _generate_response(self, system_prompt: str, user_message: str) -> str:
        """Generate response with GPT-4"""
        
        try:
            # Initialize OpenAI client with minimal config
            client = OpenAI(
                api_key=os.environ.get('OPENAI_API_KEY'),
                timeout=30.0,
                max_retries=2
            )
            
            response = client.chat.completions.create(
                model="gpt-4-turbo-preview",  # or "gpt-3.5-turbo" for lower cost
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.7,
                max_tokens=1500
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
        assistant_response: str,
        sources: List[Dict[str, str]]
    ):
        """
        Log conversation to a storage system
        
        For Vercel, we'll use KV storage or write to a file in /tmp
        For now, we'll use environment variable to store logs path
        """
        try:
            import tempfile
            from pathlib import Path
            
            # Create log entry
            log_entry = {
                'timestamp': datetime.utcnow().isoformat(),
                'session_id': session_id,
                'user_message': user_message,
                'assistant_response': assistant_response,
                'sources': [s['source'] for s in sources],
                'message_length': len(user_message),
                'response_length': len(assistant_response)
            }
            
            # For Vercel, we'll use /tmp directory (ephemeral but works for demo)
            # In production, use Vercel KV, Supabase, or other persistent storage
            log_dir = Path('/tmp/chat_logs')
            log_dir.mkdir(exist_ok=True)
            
            # Append to daily log file
            log_file = log_dir / f"chat_log_{datetime.utcnow().strftime('%Y-%m-%d')}.jsonl"
            with open(log_file, 'a') as f:
                f.write(json.dumps(log_entry) + '\n')
            
            print(f"✓ Logged conversation: {session_id}")
            
        except Exception as e:
            # Don't fail the request if logging fails
            print(f"Warning: Failed to log conversation: {e}")

