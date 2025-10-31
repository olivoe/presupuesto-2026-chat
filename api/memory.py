"""
Memory System for AI Chat - Question Tagging and Long-term Memory
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
import json
import re

class MemorySystem:
    """
    Manages question categorization and important Q&A storage
    """
    
    # Question categories and their keywords
    CATEGORIES = {
        'methodology': [
            'how', 'calculate', 'method', 'approach', 'technique', 'process',
            'baseline', 'lift', 'interest index', 'bias correction', 'model',
            'formula', 'equation', 'algorithm'
        ],
        'sentiment': [
            'sentiment', 'positive', 'negative', 'neutral', 'emotion', 'feeling',
            'opinion', 'attitude', 'mood', 'reaction'
        ],
        'interest_index': [
            'interest index', 'ranking', 'performance', 'views', 'engagement',
            'lift', 'baseline', 'top post', 'best', 'highest'
        ],
        'topics': [
            'topic', 'theme', 'subject', 'corruption', 'corrupción', 'president',
            'congress', 'budget', 'presupuesto', 'infrastructure', 'taxes'
        ],
        'accounts': [
            'account', 'user', 'creator', '@', 'mynoralfonsodelar', 'congreso',
            'who', 'which account', 'profile'
        ],
        'statistics': [
            'how many', 'count', 'number', 'percentage', 'total', 'average',
            'mean', 'median', 'distribution', 'stats'
        ],
        'recommendations': [
            'recommend', 'suggest', 'advice', 'should', 'strategy', 'approach',
            'what works', 'best practice', 'communication'
        ],
        'comparison': [
            'compare', 'difference', 'versus', 'vs', 'between', 'contrast',
            'approving', 'disapproving', 'better', 'worse'
        ]
    }
    
    # Pre-defined important Q&A pairs (seed memory)
    SEED_MEMORY = [
        {
            'question': 'What is the Interest Index?',
            'answer': 'The Interest Index measures how much a video exceeded expected performance (baseline). An Index of 1.0 means performance equal to baseline (0% lift), 2.0 means 2× baseline (100% lift), and 12.8 means 12.8× baseline (1,180% lift). It combines historical lift (vs account\'s typical performance) and relative lift (vs other posts).',
            'categories': ['methodology', 'interest_index'],
            'importance': 'high',
            'created_at': datetime.utcnow().isoformat()
        },
        {
            'question': 'How do you calculate lift percentage?',
            'answer': 'Lift % = (Interest Index - 1) × 100. For example, an Interest Index of 12.799 means 1,179.9% more views than expected, or the video achieved 1,279.9% of the baseline.',
            'categories': ['methodology', 'interest_index'],
            'importance': 'high',
            'created_at': datetime.utcnow().isoformat()
        },
        {
            'question': 'What is the overall sentiment?',
            'answer': 'The overall sentiment is extremely negative: 95.8% negative (CI: 81.5%-98.9%), 2.1% positive (CI: 0%-13.8%), and 2.1% neutral (CI: 0.9%-6.4%). This is bias-corrected data accounting for 85% extraction rate.',
            'categories': ['sentiment', 'statistics'],
            'importance': 'high',
            'created_at': datetime.utcnow().isoformat()
        },
        {
            'question': 'Which post has the highest Interest Index?',
            'answer': '@mynoralfonsodelar with Interest Index 12.80 (112,800 views, 1,179.9% lift above baseline). This is a disapproving post that significantly exceeded expectations.',
            'categories': ['interest_index', 'accounts', 'statistics'],
            'importance': 'high',
            'created_at': datetime.utcnow().isoformat()
        },
        {
            'question': 'Why are there two sentiment models?',
            'answer': 'Approving and disapproving posts have different linguistic contexts and sarcasm patterns. Model A (for approving posts) has 73.1% accuracy, while Model B (for disapproving posts) has 93.8% accuracy. Separate models improve overall classification accuracy.',
            'categories': ['methodology', 'sentiment'],
            'importance': 'high',
            'created_at': datetime.utcnow().isoformat()
        },
        {
            'question': 'What are the main topics in the comments?',
            'answer': 'Top 3 topics: 1) Corrupción (229 mentions) - institutional distrust, 2) Presidente Arévalo (159 mentions) - personalization and blame, 3) Congreso/Diputados (121 mentions) - elite capture narrative.',
            'categories': ['topics', 'statistics'],
            'importance': 'high',
            'created_at': datetime.utcnow().isoformat()
        },
        {
            'question': 'What is bias correction and why is it needed?',
            'answer': 'We extracted 85% of comments, meaning 15% are missing. Bias correction (Missing Data CI Inflation) widens confidence intervals to account for uncertainty from incomplete data. This ensures our estimates are conservative and statistically sound.',
            'categories': ['methodology', 'statistics'],
            'importance': 'high',
            'created_at': datetime.utcnow().isoformat()
        }
    ]
    
    def __init__(self):
        """Initialize memory system with seed data"""
        self.memory = self.SEED_MEMORY.copy()
    
    def categorize_question(self, question: str) -> List[str]:
        """
        Categorize a question based on keywords
        
        Returns list of matching categories
        """
        question_lower = question.lower()
        categories = []
        
        for category, keywords in self.CATEGORIES.items():
            for keyword in keywords:
                if keyword in question_lower:
                    if category not in categories:
                        categories.append(category)
                    break
        
        return categories if categories else ['general']
    
    def find_relevant_memory(self, question: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """
        Find relevant Q&A pairs from memory based on question categories
        
        Returns top_k most relevant memories
        """
        categories = self.categorize_question(question)
        
        # Score each memory based on category overlap
        scored_memories = []
        for memory in self.memory:
            memory_categories = set(memory.get('categories', []))
            query_categories = set(categories)
            
            # Calculate overlap score
            overlap = len(memory_categories & query_categories)
            
            if overlap > 0:
                # Boost score for high importance
                importance_boost = 1.5 if memory.get('importance') == 'high' else 1.0
                score = overlap * importance_boost
                
                scored_memories.append({
                    'memory': memory,
                    'score': score
                })
        
        # Sort by score and return top_k
        scored_memories.sort(key=lambda x: x['score'], reverse=True)
        return [item['memory'] for item in scored_memories[:top_k]]
    
    def add_memory(
        self,
        question: str,
        answer: str,
        importance: str = 'medium',
        custom_categories: Optional[List[str]] = None
    ):
        """
        Add a new Q&A pair to memory
        
        Args:
            question: The user's question
            answer: The assistant's answer
            importance: 'high', 'medium', or 'low'
            custom_categories: Optional list of categories (auto-detected if None)
        """
        categories = custom_categories or self.categorize_question(question)
        
        memory_entry = {
            'question': question,
            'answer': answer,
            'categories': categories,
            'importance': importance,
            'created_at': datetime.utcnow().isoformat()
        }
        
        self.memory.append(memory_entry)
        return memory_entry
    
    def get_memory_context(self, question: str, max_length: int = 500) -> str:
        """
        Get formatted memory context for inclusion in prompt
        
        Returns a string with relevant past Q&As
        """
        relevant_memories = self.find_relevant_memory(question, top_k=2)
        
        if not relevant_memories:
            return ""
        
        context = "\n=== RELEVANT PAST Q&As ===\n\n"
        
        for i, memory in enumerate(relevant_memories, 1):
            qa_text = f"Q: {memory['question']}\nA: {memory['answer']}\n"
            
            # Truncate if too long
            if len(context + qa_text) > max_length:
                break
            
            context += qa_text + "\n"
        
        return context
    
    def export_memory(self) -> str:
        """Export memory as JSON string"""
        return json.dumps(self.memory, indent=2)
    
    def import_memory(self, json_str: str):
        """Import memory from JSON string"""
        try:
            imported = json.loads(json_str)
            self.memory.extend(imported)
        except Exception as e:
            print(f"Failed to import memory: {e}")

