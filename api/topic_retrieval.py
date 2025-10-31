"""
Topic Analysis Retrieval System
"""

import json
import os
from typing import List, Dict, Any, Optional

class TopicRetrieval:
    """
    Retrieves topic analysis data and psychosocial insights
    """
    
    def __init__(self):
        """Initialize topic retrieval system"""
        self.topic_data = None
        self.psychosocial_insights = None
        self.sentiment_by_topic = None
        self._load_data()
    
    def _load_data(self):
        """Load topic analysis data"""
        try:
            # Load topic analysis (TF-IDF, LDA, NMF)
            topic_path = os.path.join(os.path.dirname(__file__), '../data/topics/topic_analysis.json')
            if os.path.exists(topic_path):
                with open(topic_path, 'r', encoding='utf-8') as f:
                    self.topic_data = json.load(f)
                print(f"Loaded topic analysis data")
            
            # Load psychosocial insights
            insights_path = os.path.join(os.path.dirname(__file__), '../data/topics/psychosocial_insights.txt')
            if os.path.exists(insights_path):
                with open(insights_path, 'r', encoding='utf-8') as f:
                    self.psychosocial_insights = f.read()
                print(f"Loaded psychosocial insights ({len(self.psychosocial_insights)} chars)")
            
            # Load sentiment by topic
            sentiment_path = os.path.join(os.path.dirname(__file__), '../data/sentiment/sentiment_by_topic.json')
            if os.path.exists(sentiment_path):
                with open(sentiment_path, 'r', encoding='utf-8') as f:
                    self.sentiment_by_topic = json.load(f)
                print(f"Loaded sentiment by topic ({len(self.sentiment_by_topic)} topics)")
            
        except Exception as e:
            print(f"Error loading topic data: {e}")
            import traceback
            traceback.print_exc()
    
    def get_top_keywords_by_sentiment(self, sentiment: str, top_n: int = 10) -> List[str]:
        """
        Get top TF-IDF keywords for a sentiment
        
        Args:
            sentiment: 'negative', 'positive', or 'neutral'
            top_n: Number of keywords to return
            
        Returns:
            List of keywords
        """
        if not self.topic_data or 'tfidf' not in self.topic_data:
            return []
        
        tfidf_data = self.topic_data['tfidf']
        if sentiment not in tfidf_data:
            return []
        
        # Get top keywords
        keywords = tfidf_data[sentiment].get('top_keywords', [])
        return keywords[:top_n]
    
    def get_lda_topics(self, sentiment: str, top_n: int = 5) -> List[Dict[str, Any]]:
        """
        Get LDA topics for a sentiment
        
        Args:
            sentiment: 'negative', 'positive', or 'neutral'
            top_n: Number of topics to return
            
        Returns:
            List of topic dictionaries
        """
        if not self.topic_data or 'lda' not in self.topic_data:
            return []
        
        lda_data = self.topic_data['lda']
        if sentiment not in lda_data:
            return []
        
        topics = lda_data[sentiment].get('topics', [])
        return topics[:top_n]
    
    def get_topic_stats(self, topic_name: str) -> Optional[Dict[str, Any]]:
        """
        Get statistics for a specific topic
        
        Args:
            topic_name: Topic name (e.g., 'salud', 'educacion')
            
        Returns:
            Topic statistics or None
        """
        if not self.sentiment_by_topic:
            return None
        
        return self.sentiment_by_topic.get(topic_name)
    
    def get_all_topics_summary(self) -> Dict[str, Any]:
        """
        Get summary of all tracked topics
        
        Returns:
            Dictionary with topic summaries
        """
        if not self.sentiment_by_topic:
            return {}
        
        summary = {
            'total_topics': len(self.sentiment_by_topic),
            'topics': []
        }
        
        for topic_name, topic_data in self.sentiment_by_topic.items():
            summary['topics'].append({
                'name': topic_name,
                'total_comments': topic_data['total'],
                'pct_negative': topic_data['pct_negative'],
                'pct_positive': topic_data['pct_positive']
            })
        
        # Sort by total comments descending
        summary['topics'] = sorted(
            summary['topics'],
            key=lambda x: x['total_comments'],
            reverse=True
        )
        
        return summary
    
    def get_psychosocial_context(self, query: str) -> str:
        """
        Get relevant psychosocial insights based on query
        
        Args:
            query: User's question
            
        Returns:
            Relevant excerpt or full insights
        """
        if not self.psychosocial_insights:
            return ""
        
        query_lower = query.lower()
        
        # If asking about psychosocial themes or "why"
        if any(word in query_lower for word in ['psico', 'social', 'por que', 'why', 'razon', 'tema', 'theme']):
            # Return relevant excerpt (first 1000 chars for now)
            return self.psychosocial_insights[:1000] + "...\n"
        
        return ""
    
    def get_topic_context(self, query: str) -> str:
        """
        Generate context for LLM based on topic-related query
        
        Args:
            query: User's question
            
        Returns:
            Formatted context string
        """
        query_lower = query.lower()
        context = ""
        
        # Topic summary queries
        if any(word in query_lower for word in ['temas', 'topics', 'principales', 'main', 'top']):
            summary = self.get_all_topics_summary()
            if summary and 'topics' in summary:
                context += "\n=== TEMAS PRINCIPALES ===\n\n"
                context += f"**Total de temas rastreados: {summary['total_topics']}**\n\n"
                
                context += "**Top 10 temas por frecuencia:**\n"
                for i, topic in enumerate(summary['topics'][:10], 1):
                    context += f"{i}. **{topic['name'].capitalize()}**: {topic['total_comments']} comentarios "
                    context += f"({topic['pct_negative']:.1f}% neg, {topic['pct_positive']:.1f}% pos)\n"
                context += "\n"
        
        # Keyword queries
        if any(word in query_lower for word in ['palabra', 'keyword', 'termino', 'frecuent']):
            # Get keywords for negative (most common)
            keywords = self.get_top_keywords_by_sentiment('negative', top_n=15)
            if keywords:
                context += "\n=== PALABRAS CLAVE MÁS FRECUENTES (Negativos) ===\n\n"
                context += ", ".join(keywords) + "\n\n"
        
        # Psychosocial insights queries
        if any(word in query_lower for word in ['psico', 'social', 'por que', 'razon', 'insight']):
            insights = self.get_psychosocial_context(query)
            if insights:
                context += "\n=== ANÁLISIS PSICOSOCIAL ===\n\n"
                context += insights + "\n"
        
        # Specific topic query
        for topic_name in ['salud', 'educacion', 'infraestructura', 'corrupcion', 'congreso', 'presidente']:
            if topic_name in query_lower:
                topic_stats = self.get_topic_stats(topic_name)
                if topic_stats:
                    context += f"\n=== TEMA: {topic_name.upper()} ===\n\n"
                    context += f"- Comentarios: {topic_stats['total']}\n"
                    context += f"- Negativos: {topic_stats['negative']} ({topic_stats['pct_negative']}%)\n"
                    context += f"- Positivos: {topic_stats['positive']} ({topic_stats['pct_positive']}%)\n"
                    context += f"- Neutrales: {topic_stats['neutral']} ({topic_stats['pct_neutral']}%)\n\n"
                break
        
        if context:
            context += "Fuente: Análisis de temas en 2,042 comentarios sobre Presupuesto 2026.\n"
        
        return context

