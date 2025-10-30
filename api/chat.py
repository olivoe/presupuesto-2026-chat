"""
Vercel Serverless Function for Chat API
"""

from http.server import BaseHTTPRequestHandler
import json
import os
from typing import List, Dict, Any
import openai

# Initialize OpenAI client
from openai import OpenAI
client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))

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
            
            # Get embedding for the query
            query_embedding = self._get_embedding(message)
            
            # Retrieve relevant context (using pre-built knowledge base)
            contexts = self._retrieve_context(query_embedding, top_k=5)
            
            # Build prompt
            prompt = self._build_prompt(message, contexts, conversation_history)
            
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
    
    def _get_embedding(self, text: str) -> List[float]:
        """Get embedding for text"""
        try:
            response = client.embeddings.create(
                model="text-embedding-3-small",
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            print(f"Error getting embedding: {e}")
            return [0.0] * 1536
    
    def _retrieve_context(self, query_embedding: List[float], top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Retrieve relevant context from knowledge base
        
        For Vercel, we'll use a simplified approach with static context
        or integrate with Pinecone/Supabase for vector search
        """
        
        # Load pre-computed knowledge base summaries from environment or file
        # For now, return static high-level context
        
        contexts = [
            {
                'text': """Presupuesto 2026 Analysis Overview:
                - 24 TikTok posts analyzed about Guatemala's 2026 budget
                - 2,042 comments extracted and analyzed
                - Extreme negative sentiment: 95.9% negative (1,957 comments)
                - Only 2.1% positive (43 comments), 2.1% neutral (42 comments)
                - Interest Index calculated with historical and relative lift
                - Topic analysis shows corruption (229 mentions) as #1 concern
                """,
                'metadata': {'source': 'Project Overview', 'type': 'summary'}
            },
            {
                'text': """Sentiment Analysis Findings:
                - Dual model approach: separate models for approving vs disapproving posts
                - Model A (approving posts): 73.1% accuracy
                - Model B (disapproving posts): 93.8% accuracy
                - Training: 172 manually annotated comments
                - Extreme polarization: overwhelming negativity across all posts
                - Weighted by likes: negative comments receive more engagement
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
            }
        ]
        
        return contexts[:top_k]
    
    def _build_prompt(
        self,
        query: str,
        contexts: List[Dict[str, Any]],
        conversation_history: List[Dict[str, str]]
    ) -> str:
        """Build prompt for LLM"""
        
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

Answer in the same language as the question (English or Spanish).
"""
        
        # Build context section
        context_section = "\n\n=== RELEVANT CONTEXT ===\n\n"
        for i, ctx in enumerate(contexts, 1):
            context_section += f"[Context {i}]:\n{ctx['text']}\n\n"
        
        # Build conversation history
        history_section = ""
        if conversation_history:
            history_section = "\n\n=== CONVERSATION HISTORY ===\n\n"
            for msg in conversation_history[-4:]:  # Last 4 messages
                role = msg.get('role', 'user')
                content = msg.get('content', '')
                history_section += f"{role.upper()}: {content}\n\n"
        
        prompt = system_prompt + context_section + history_section
        
        return prompt
    
    def _generate_response(self, system_prompt: str, user_message: str) -> str:
        """Generate response with GPT-4"""
        
        try:
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
            return f"I apologize, but I encountered an error: {str(e)}"

