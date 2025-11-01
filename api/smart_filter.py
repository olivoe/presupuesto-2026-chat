"""
Smart Pre-filtering System - Option B
Filters comments to relevant subset (50-200) based on query keywords
"""

import json
import re
from typing import List, Dict, Any, Tuple
import os

class SmartFilter:
    """
    Intelligently filters comments based on query to create focused dataset
    """
    
    # Comprehensive keyword mappings
    KEYWORD_MAP = {
        # Health
        'salud': ['salud', 'hospital', 'medicina', 'medico', 'doctor', 'igss', 'enferm', 'clinic', 'medicamento'],
        
        # Education
        'educacion': ['educacion', 'educación', 'escuela', 'maestro', 'profesor', 'estudiante', 'colegio', 'universidad'],
        
        # Infrastructure
        'infraestructura': ['infraestructura', 'carretera', 'calle', 'puente', 'camino', 'paviment', 'construccion', 'construcción', 'obra'],
        
        # Corruption
        'corrupcion': ['corrupc', 'corrupt', 'robo', 'robar', 'ladron', 'ladrón', 'malversa', 'fraude'],
        
        # Taxes
        'impuestos': ['impuesto', 'tax', 'sat', 'tribut', 'fiscal'],
        
        # Poverty / Social
        'pobreza': ['pobreza', 'pobre', 'hambre', 'miseria', 'necesidad', 'ayuda'],
        
        # Congress / Deputies
        'congreso': ['congreso', 'diputado', 'legisl', 'bancada'],
        
        # President / Government
        'presidente': ['presidente', 'gobierno', 'ejecutivo', 'ministro', 'giammattei', 'arévalo', 'arevalo'],
        
        # Budget specific
        'presupuesto': ['presupuesto', 'budget', 'fondos', 'dinero publico', 'dinero público', 'recursos'],
        
        # Approval / Support
        'aprobacion': ['aprob', 'aprueba', 'aprobacion', 'aprobación', 'apoyo', 'favor', 'bien', 'bueno'],
        
        # Disapproval / Against
        'desaprobacion': ['desaprob', 'contra', 'mal', 'malo', 'rechazo', 'no sirve'],
        
        # Quality of life
        'calidad_vida': ['calidad', 'vida', 'vivir', 'bienestar'],
        
        # Food / Basic needs
        'alimentos': ['alimento', 'comida', 'comer', 'canasta', 'basica', 'básica', 'precio'],
        
        # Transportation
        'transporte': ['transporte', 'bus', 'camion', 'camión', 'transmetro', 'movilidad'],
        
        # Security
        'seguridad': ['seguridad', 'policia', 'policía', 'crimen', 'delincuencia', 'violencia'],
        
        # Employment
        'empleo': ['empleo', 'trabajo', 'desempleo', 'desempleado', 'empleado', 'trabajador'],
        
        # Salary / Wages
        'salario': ['salario', 'sueldo', 'pago', 'salario minimo', 'salario mínimo', 'ingreso']
    }
    
    def __init__(self):
        """Initialize smart filter"""
        self.comments = []
        self._load_comments()
    
    def _load_comments(self):
        """Load all comments from JSON file"""
        try:
            # Try data directory first (new structure)
            data_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'comments', 'comments_all.json')
            if os.path.exists(data_path):
                with open(data_path, 'r', encoding='utf-8') as f:
                    self.comments = json.load(f)
                print(f"✓ Loaded {len(self.comments)} comments from data/comments/")
                return
            
            # Fallback to old location
            old_path = os.path.join(os.path.dirname(__file__), 'comments_data.json')
            if os.path.exists(old_path):
                with open(old_path, 'r', encoding='utf-8') as f:
                    self.comments = json.load(f)
                print(f"✓ Loaded {len(self.comments)} comments from api/")
                return
            
            print("⚠ Warning: No comments file found")
            
        except Exception as e:
            print(f"Error loading comments: {e}")
            self.comments = []
    
    def extract_keywords(self, query: str) -> List[str]:
        """
        Extract relevant keywords from user query
        Returns list of search terms
        """
        query_lower = query.lower()
        keywords = []
        
        # Check each category
        for category, terms in self.KEYWORD_MAP.items():
            for term in terms:
                if term in query_lower:
                    # Add the term itself
                    keywords.append(term)
                    # Also add related terms from same category
                    keywords.extend([t for t in terms if t not in keywords])
                    break
        
        # If no keywords found, extract words from query (fallback)
        if not keywords:
            # Remove common words
            stop_words = {'el', 'la', 'los', 'las', 'de', 'del', 'al', 'en', 'con', 'por', 'para', 
                         'que', 'qué', 'como', 'cómo', 'hay', 'sobre', 'ese', 'esa', 'esos', 'esas',
                         'un', 'una', 'unos', 'unas', 'es', 'son', 'está', 'están', 'ser', 'estar',
                         'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of',
                         'cuantos', 'cuantas', 'cuántos', 'cuántas', 'dame', 'muestra', 'muestrame',
                         'comentarios', 'ejemplos', 'gente', 'personas', 'piensa', 'piensan', 'dice', 'dicen'}
            
            words = re.findall(r'\b\w{4,}\b', query_lower)  # Words with 4+ chars
            keywords = [w for w in words if w not in stop_words]
        
        return list(set(keywords))  # Remove duplicates
    
    def filter_comments(self, query: str, max_comments: int = 200, min_comments: int = 50) -> Tuple[List[Dict], List[str]]:
        """
        Filter comments based on query keywords
        Returns (filtered_comments, keywords_used)
        """
        if not self.comments:
            return [], []
        
        # Extract keywords
        keywords = self.extract_keywords(query)
        
        if not keywords:
            # No keywords - return random sample
            import random
            sample_size = min(max_comments, len(self.comments))
            return random.sample(self.comments, sample_size), []
        
        # Filter comments that match ANY keyword
        filtered = []
        for comment in self.comments:
            text = comment.get('text', '').lower()
            # Check if any keyword appears in comment
            if any(keyword in text for keyword in keywords):
                filtered.append(comment)
        
        # If too many results, prioritize by relevance
        if len(filtered) > max_comments:
            # Score by number of keyword matches
            scored = []
            for comment in filtered:
                text = comment.get('text', '').lower()
                score = sum(1 for keyword in keywords if keyword in text)
                scored.append((score, comment))
            
            # Sort by score (descending) and take top max_comments
            scored.sort(key=lambda x: x[0], reverse=True)
            filtered = [comment for score, comment in scored[:max_comments]]
        
        # If too few results, expand search
        if len(filtered) < min_comments and len(filtered) < len(self.comments):
            # Add random comments to reach min_comments
            remaining = [c for c in self.comments if c not in filtered]
            import random
            needed = min(min_comments - len(filtered), len(remaining))
            filtered.extend(random.sample(remaining, needed))
        
        return filtered, keywords
    
    def calculate_statistics(self, comments: List[Dict]) -> Dict[str, Any]:
        """
        Calculate statistics on filtered comment set
        """
        if not comments:
            return {
                'total': 0,
                'positive': 0,
                'negative': 0,
                'neutral': 0,
                'pct_positive': 0.0,
                'pct_negative': 0.0,
                'pct_neutral': 0.0
            }
        
        # Count by sentiment
        sentiments = {'positive': 0, 'negative': 0, 'neutral': 0}
        for comment in comments:
            sentiment = comment.get('sentiment', 'neutral').lower()
            if sentiment in sentiments:
                sentiments[sentiment] += 1
        
        total = len(comments)
        
        return {
            'total': total,
            'positive': sentiments['positive'],
            'negative': sentiments['negative'],
            'neutral': sentiments['neutral'],
            'pct_positive': round(sentiments['positive'] / total * 100, 1) if total > 0 else 0.0,
            'pct_negative': round(sentiments['negative'] / total * 100, 1) if total > 0 else 0.0,
            'pct_neutral': round(sentiments['neutral'] / total * 100, 1) if total > 0 else 0.0
        }
    
    def get_examples_by_sentiment(self, comments: List[Dict], sentiment: str, limit: int = 5) -> List[Dict]:
        """
        Get example comments of specific sentiment from filtered set
        """
        matching = [c for c in comments if c.get('sentiment', '').lower() == sentiment.lower()]
        return matching[:limit]
    
    def create_context_for_llm(self, query: str) -> str:
        """
        Main method: Filter comments and create rich context for LLM
        """
        # Filter comments
        filtered_comments, keywords = self.filter_comments(query)
        
        if not filtered_comments:
            return "No se encontraron comentarios relevantes en la base de datos."
        
        # Calculate statistics
        stats = self.calculate_statistics(filtered_comments)
        
        # Build context
        context_parts = []
        
        # Header
        context_parts.append("=== DATOS REALES FILTRADOS ===")
        context_parts.append(f"Búsqueda basada en: {', '.join(keywords) if keywords else 'muestra general'}")
        context_parts.append(f"Total de comentarios relevantes: {stats['total']}")
        context_parts.append("")
        
        # Statistics
        context_parts.append("ESTADÍSTICAS DE SENTIMIENTO:")
        context_parts.append(f"- Positivos: {stats['positive']} ({stats['pct_positive']}%)")
        context_parts.append(f"- Negativos: {stats['negative']} ({stats['pct_negative']}%)")
        context_parts.append(f"- Neutrales: {stats['neutral']} ({stats['pct_neutral']}%)")
        context_parts.append("")
        
        # Examples by sentiment
        for sentiment, label in [('positive', 'POSITIVOS'), ('negative', 'NEGATIVOS'), ('neutral', 'NEUTRALES')]:
            examples = self.get_examples_by_sentiment(filtered_comments, sentiment, limit=10)
            if examples:
                context_parts.append(f"EJEMPLOS DE COMENTARIOS {label}:")
                for i, comment in enumerate(examples, 1):
                    text = comment.get('text', '').strip()
                    post = comment.get('post_url', 'N/A')
                    context_parts.append(f"{i}. \"{text}\" (Post: {post})")
                context_parts.append("")
        
        # Footer instruction
        context_parts.append("INSTRUCCIONES CRÍTICAS:")
        context_parts.append("1. USA EXACTAMENTE estos comentarios reales cuando des ejemplos")
        context_parts.append("2. USA estas estadísticas exactas para responder preguntas de conteo")
        context_parts.append("3. NUNCA inventes o generalices comentarios")
        context_parts.append("4. Si necesitas más ejemplos, usa SOLO los de esta lista")
        
        return "\n".join(context_parts)


# Singleton instance
_smart_filter = None

def get_smart_filter() -> SmartFilter:
    """Get or create smart filter instance"""
    global _smart_filter
    if _smart_filter is None:
        _smart_filter = SmartFilter()
    return _smart_filter

