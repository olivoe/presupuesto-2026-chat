"""
Post & Interest Index Retrieval System
"""

import json
import os
from typing import List, Dict, Any, Optional

class PostRetrieval:
    """
    Retrieves post metadata and Interest Index data
    """
    
    def __init__(self):
        """Initialize post retrieval system"""
        self.posts_data = None
        self.interest_data = None
        self._load_data()
    
    def _load_data(self):
        """Load post and interest index data"""
        try:
            # Load posts metadata
            posts_path = os.path.join(os.path.dirname(__file__), '../data/posts/posts_metadata.json')
            if os.path.exists(posts_path):
                with open(posts_path, 'r', encoding='utf-8') as f:
                    self.posts_data = json.load(f)
                print(f"Loaded {len(self.posts_data)} posts from posts_metadata.json")
            
            # Load interest index
            interest_path = os.path.join(os.path.dirname(__file__), '../data/posts/interest_index.json')
            if os.path.exists(interest_path):
                with open(interest_path, 'r', encoding='utf-8') as f:
                    self.interest_data = json.load(f)
                print(f"Loaded {len(self.interest_data)} interest index entries")
            
        except Exception as e:
            print(f"Error loading post data: {e}")
            import traceback
            traceback.print_exc()
    
    def get_top_posts_by_interest(self, top_n: int = 10) -> List[Dict[str, Any]]:
        """
        Get top posts ranked by Interest Index
        
        Args:
            top_n: Number of top posts to return
            
        Returns:
            List of posts with Interest Index data
        """
        if not self.interest_data:
            return []
        
        # Sort by interest_index descending
        sorted_posts = sorted(
            self.interest_data,
            key=lambda x: x.get('interest_index', 0),
            reverse=True
        )
        
        return sorted_posts[:top_n]
    
    def get_post_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """
        Get post metadata for a specific username
        
        Args:
            username: Account username (with or without @)
            
        Returns:
            Post data or None
        """
        if not self.posts_data:
            return None
        
        # Normalize username
        username_clean = username.lstrip('@')
        
        for post in self.posts_data:
            if post.get('username', '').lstrip('@') == username_clean:
                return post
        
        return None
    
    def get_posts_by_stance(self, stance: str) -> List[Dict[str, Any]]:
        """
        Get all posts with a specific stance
        
        Args:
            stance: 'approving' or 'disapproving'
            
        Returns:
            List of matching posts
        """
        if not self.posts_data:
            return []
        
        return [p for p in self.posts_data if p.get('post_stance') == stance]
    
    def get_engagement_stats(self) -> Dict[str, Any]:
        """
        Get aggregate engagement statistics
        
        Returns:
            Dictionary with engagement stats
        """
        if not self.posts_data:
            return {}
        
        import pandas as pd
        df = pd.DataFrame(self.posts_data)
        
        stats = {
            'total_posts': len(df),
            'total_views': int(df['views'].sum()) if 'views' in df.columns else 0,
            'total_likes': int(df['likes'].sum()) if 'likes' in df.columns else 0,
            'total_comments': int(df['comments'].sum()) if 'comments' in df.columns else 0,
            'total_shares': int(df['shares'].sum()) if 'shares' in df.columns else 0,
            'avg_views': float(df['views'].mean()) if 'views' in df.columns else 0,
            'avg_likes': float(df['likes'].mean()) if 'likes' in df.columns else 0,
            'by_stance': {}
        }
        
        # Engagement by stance
        for stance in df['post_stance'].unique():
            if pd.notna(stance):
                stance_df = df[df['post_stance'] == stance]
                stats['by_stance'][stance] = {
                    'count': len(stance_df),
                    'total_views': int(stance_df['views'].sum()) if 'views' in stance_df.columns else 0,
                    'avg_views': float(stance_df['views'].mean()) if 'views' in stance_df.columns else 0
                }
        
        return stats
    
    def get_post_context(self, query: str) -> str:
        """
        Generate context for LLM based on post-related query
        
        Args:
            query: User's question
            
        Returns:
            Formatted context string
        """
        query_lower = query.lower()
        context = "\n=== DATOS DE POSTS Y ENGAGEMENT ===\n\n"
        
        # Interest Index queries
        if any(word in query_lower for word in ['interest index', 'indice', 'ranking', 'mejor', 'peor', 'top']):
            top_posts = self.get_top_posts_by_interest(top_n=10)
            if top_posts:
                context += "**Top 10 Posts por Interest Index:**\n\n"
                for i, post in enumerate(top_posts, 1):
                    context += f"{i}. @{post.get('username', 'N/A')} - Interest Index: {post.get('interest_index', 0):.3f}\n"
                    if 'historical_lift' in post:
                        context += f"   - Historical Lift: {post.get('historical_lift', 'N/A')}\n"
                    if 'relative_lift' in post:
                        context += f"   - Relative Lift: {post.get('relative_lift', 'N/A')}\n"
                context += "\n"
        
        # Engagement queries
        if any(word in query_lower for word in ['engagement', 'views', 'likes', 'comentarios', 'shares']):
            stats = self.get_engagement_stats()
            if stats:
                context += "**Estadísticas de Engagement:**\n\n"
                context += f"- Total posts: {stats['total_posts']}\n"
                context += f"- Total views: {stats['total_views']:,}\n"
                context += f"- Total likes: {stats['total_likes']:,}\n"
                context += f"- Total comentarios: {stats['total_comments']:,}\n"
                context += f"- Promedio views: {stats['avg_views']:,.0f}\n"
                context += f"- Promedio likes: {stats['avg_likes']:,.0f}\n\n"
                
                if 'by_stance' in stats and stats['by_stance']:
                    context += "**Por Stance:**\n"
                    for stance, stance_stats in stats['by_stance'].items():
                        context += f"- {stance.capitalize()}: {stance_stats['count']} posts, "
                        context += f"{stance_stats['total_views']:,} views totales\n"
                    context += "\n"
        
        # Stance queries
        if any(word in query_lower for word in ['approving', 'disapproving', 'favor', 'contra', 'apoyo']):
            if 'aproving' in query_lower or 'favor' in query_lower or 'apoyo' in query_lower:
                posts = self.get_posts_by_stance('approving')
                if posts:
                    context += f"**Posts Approving (a favor): {len(posts)} posts**\n\n"
            elif 'disapproving' in query_lower or 'contra' in query_lower:
                posts = self.get_posts_by_stance('disapproving')
                if posts:
                    context += f"**Posts Disapproving (en contra): {len(posts)} posts**\n\n"
        
        context += "Fuente: Análisis de 21 posts de TikTok sobre Presupuesto 2026.\n"
        
        return context if len(context) > 100 else ""

