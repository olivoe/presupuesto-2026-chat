"""
Full Dataset Loader for Option A
Loads all 2,042 comments into the prompt context
"""

import json
import os
from typing import List, Dict, Any

class FullDatasetLoader:
    """
    Loads complete dataset of comments for comprehensive analysis
    """
    
    def __init__(self):
        """Initialize and load all comments"""
        self.comments = []
        self.posts = []
        self._load_all_data()
    
    def _load_all_data(self):
        """Load all comments and post metadata"""
        try:
            # Load comments
            comments_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'comments', 'comments_all.json')
            if os.path.exists(comments_path):
                with open(comments_path, 'r', encoding='utf-8') as f:
                    self.comments = json.load(f)
                print(f"✓ Loaded {len(self.comments)} comments")
            else:
                print(f"⚠ Warning: Comments file not found at {comments_path}")
            
            # Load post metadata (Interest Index, etc.)
            posts_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'posts', 'posts_metadata.json')
            if os.path.exists(posts_path):
                with open(posts_path, 'r', encoding='utf-8') as f:
                    self.posts = json.load(f)
                print(f"✓ Loaded {len(self.posts)} posts metadata")
            else:
                print(f"⚠ Warning: Posts metadata file not found")
                self.posts = []
                
        except Exception as e:
            print(f"Error loading data: {e}")
            self.comments = []
            self.posts = []
    
    def get_statistics(self) -> Dict[str, Any]:
        """Calculate overall statistics"""
        if not self.comments:
            return {}
        
        total = len(self.comments)
        sentiments = {'positive': 0, 'negative': 0, 'neutral': 0}
        
        for comment in self.comments:
            sentiment = comment.get('sentiment', 'neutral').lower()
            if sentiment in sentiments:
                sentiments[sentiment] += 1
        
        return {
            'total_comments': total,
            'positive': sentiments['positive'],
            'negative': sentiments['negative'],
            'neutral': sentiments['neutral'],
            'pct_positive': round(sentiments['positive'] / total * 100, 1) if total > 0 else 0.0,
            'pct_negative': round(sentiments['negative'] / total * 100, 1) if total > 0 else 0.0,
            'pct_neutral': round(sentiments['neutral'] / total * 100, 1) if total > 0 else 0.0
        }
    
    def create_full_context(self, query: str = "") -> str:
        """
        Create comprehensive context with ALL comments for LLM
        This is the core of Option A
        """
        if not self.comments:
            return "No comments data available."
        
        context_parts = []
        
        # Header
        context_parts.append("="*80)
        context_parts.append("COMPLETE DATASET - ALL 2,042 COMMENTS")
        context_parts.append("="*80)
        context_parts.append("")
        
        # Overall statistics
        stats = self.get_statistics()
        context_parts.append("OVERALL SENTIMENT DISTRIBUTION:")
        context_parts.append(f"- Total Comments: {stats['total_comments']}")
        context_parts.append(f"- Positive: {stats['positive']} ({stats['pct_positive']}%)")
        context_parts.append(f"- Negative: {stats['negative']} ({stats['pct_negative']}%)")
        context_parts.append(f"- Neutral: {stats['neutral']} ({stats['pct_neutral']}%)")
        context_parts.append("")
        context_parts.append("="*80)
        context_parts.append("ALL COMMENTS (with metadata):")
        context_parts.append("="*80)
        context_parts.append("")
        
        # All comments in structured format
        for i, comment in enumerate(self.comments, 1):
            text = comment.get('text', '').strip()
            sentiment = comment.get('sentiment', 'neutral').upper()
            post_url = comment.get('post_url', 'N/A')
            post_stance = comment.get('post_stance', 'N/A')
            likes = comment.get('likes', 0)
            confidence = comment.get('confidence', 0.0)
            
            # Compact format to save tokens
            context_parts.append(
                f"{i}. [{sentiment}] \"{text}\" "
                f"(Post: {post_url}, Stance: {post_stance}, Likes: {likes}, Confidence: {confidence:.2f})"
            )
        
        context_parts.append("")
        context_parts.append("="*80)
        context_parts.append("END OF DATASET")
        context_parts.append("="*80)
        
        return "\n".join(context_parts)
    
    def create_compact_context(self) -> str:
        """
        Create ULTRA-COMPACT version to save tokens (Option A1)
        Target: ~35,000-40,000 tokens (60% reduction)
        """
        if not self.comments:
            return "No comments data available."
        
        context_parts = []
        
        # Minimal header
        stats = self.get_statistics()
        context_parts.append(f"DATA:{stats['total_comments']}|N:{stats['pct_negative']}%|P:{stats['pct_positive']}%|U:{stats['pct_neutral']}%")
        context_parts.append("FMT:[S]txt|postID|st|L")
        context_parts.append("S:N/P/U st:A/D L:likes(if>0)")
        context_parts.append("")
        
        # Extract post ID from URL for compression
        def get_post_id(url):
            """Extract video ID from TikTok URL"""
            try:
                if '/video/' in url:
                    return url.split('/video/')[-1].split('?')[0]
                return 'UNK'
            except:
                return 'UNK'
        
        # All comments in ultra-compact format
        for comment in self.comments:
            text = comment.get('text', '').strip()
            
            # Abbreviate sentiment
            sentiment = comment.get('sentiment', 'neutral').lower()
            s = 'N' if sentiment == 'negative' else ('P' if sentiment == 'positive' else 'U')
            
            # Get post ID instead of full URL
            post_url = comment.get('post_url', 'N/A')
            post_id = get_post_id(post_url)
            
            # Abbreviate stance
            stance = comment.get('post_stance', 'N/A').lower()
            st = 'A' if 'approv' in stance else ('D' if 'disapprov' in stance else 'U')
            
            likes = comment.get('likes', 0)
            
            # Ultra-compact format: only include likes if > 0
            if likes > 0:
                context_parts.append(f"[{s}]\"{text}\"|{post_id}|{st}|{likes}L")
            else:
                context_parts.append(f"[{s}]\"{text}\"|{post_id}|{st}")
        
        return "\n".join(context_parts)
    
    def get_post_metadata_context(self) -> str:
        """Get Interest Index and post metadata"""
        if not self.posts:
            return ""
        
        context_parts = []
        context_parts.append("\n" + "="*80)
        context_parts.append("POST METADATA (Interest Index Rankings)")
        context_parts.append("="*80)
        context_parts.append("")
        
        for post in self.posts:
            context_parts.append(
                f"- {post.get('username', 'N/A')}: Interest Index {post.get('interest_index', 0):.2f}, "
                f"{post.get('views', 0):,} views, Stance: {post.get('stance', 'N/A')}"
            )
        
        return "\n".join(context_parts)


# Singleton instance
_full_dataset_loader = None

def get_full_dataset_loader() -> FullDatasetLoader:
    """Get or create full dataset loader instance"""
    global _full_dataset_loader
    if _full_dataset_loader is None:
        _full_dataset_loader = FullDatasetLoader()
    return _full_dataset_loader

