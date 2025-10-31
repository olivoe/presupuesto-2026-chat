"""
Comment Retrieval System - Access real comments from the dataset
"""

import csv
from typing import List, Dict, Any
import re
import os

class CommentRetrieval:
    """
    Retrieves real comments from the dataset based on filters
    """
    
    # Topic-Sentiment Statistics (from 2,042 analyzed comments)
    TOPIC_STATS = {
        'salud': {
            'total': 32,
            'negative': 27, 'positive': 4, 'neutral': 1,
            'pct_negative': 84.4, 'pct_positive': 12.5, 'pct_neutral': 3.1
        },
        'educacion': {
            'total': 20,
            'negative': 18, 'positive': 1, 'neutral': 1,
            'pct_negative': 90.0, 'pct_positive': 5.0, 'pct_neutral': 5.0
        },
        'infraestructura': {
            'total': 67,
            'negative': 66, 'positive': 1, 'neutral': 0,
            'pct_negative': 98.5, 'pct_positive': 1.5, 'pct_neutral': 0.0
        },
        'corrupcion': {
            'total': 275,
            'negative': 265, 'positive': 3, 'neutral': 7,
            'pct_negative': 96.4, 'pct_positive': 1.1, 'pct_neutral': 2.5
        },
        'impuestos': {
            'total': 27,
            'negative': 26, 'positive': 1, 'neutral': 0,
            'pct_negative': 96.3, 'pct_positive': 3.7, 'pct_neutral': 0.0
        },
        'pobreza': {
            'total': 28,
            'negative': 26, 'positive': 1, 'neutral': 1,
            'pct_negative': 92.9, 'pct_positive': 3.6, 'pct_neutral': 3.6
        },
        'congreso': {
            'total': 106,
            'negative': 102, 'positive': 2, 'neutral': 2,
            'pct_negative': 96.2, 'pct_positive': 1.9, 'pct_neutral': 1.9
        },
        'presidente': {
            'total': 169,
            'negative': 163, 'positive': 5, 'neutral': 1,
            'pct_negative': 96.4, 'pct_positive': 3.0, 'pct_neutral': 0.6
        }
    }
    
    # STATIC SAMPLE_COMMENTS REMOVED - ONLY USE REAL DATA FROM comments_all.json
    # No fabricated examples allowed under any circumstances
    
    def __init__(self):
        """Initialize comment retrieval system"""
        
        # Try to load the full comments CSV (for dynamic search)
        self.comments_df = None
        self._load_comments_csv()
        
        # Map Spanish topic names to internal keys
        self.topic_map = {
            'salud': 'salud',
            'health': 'salud',
            'hospitales': 'salud',
            'hospital': 'salud',
            'medicina': 'salud',
            'medico': 'salud',
            'igss': 'salud',
            'educacion': 'educacion',
            'education': 'educacion',
            'escuela': 'educacion',
            'maestro': 'educacion',
            'infraestructura': 'infraestructura',
            'infrastructure': 'infraestructura',
            'carretera': 'infraestructura',
            'calle': 'infraestructura',
            'corrupcion': 'corrupcion',
            'corruption': 'corrupcion',
            'robo': 'corrupcion',
            'impuesto': 'impuestos',
            'impuestos': 'impuestos',
            'tax': 'impuestos',
            'sat': 'impuestos',
            'pobreza': 'pobreza',
            'poverty': 'pobreza',
            'hambre': 'pobreza',
            'congreso': 'congreso',
            'congress': 'congreso',
            'diputado': 'congreso',
            'presidente': 'presidente',
            'president': 'presidente',
            'arevalo': 'presidente',
            'arévalo': 'presidente'
        }
    
    def _load_comments_csv(self):
        """Load the full comments data for dynamic searching"""
        try:
            import json
            
            # Try to load from JSON file (works in Vercel) - NEW LOCATION
            json_path = os.path.join(os.path.dirname(__file__), '../data/comments/comments_all.json')
            
            # Fallback to old location for backwards compatibility
            if not os.path.exists(json_path):
                json_path = os.path.join(os.path.dirname(__file__), 'comments_data.json')
            
            if os.path.exists(json_path):
                with open(json_path, 'r', encoding='utf-8') as f:
                    comments_list = json.load(f)
                
                # Convert to pandas DataFrame
                import pandas as pd
                self.comments_df = pd.DataFrame(comments_list)
                # Rename for compatibility
                if 'sentiment' in self.comments_df.columns:
                    self.comments_df['predicted_sentiment_ml_v3'] = self.comments_df['sentiment']
                if 'text' in self.comments_df.columns:
                    self.comments_df['comment_text'] = self.comments_df['text']
                
                print(f"Loaded {len(self.comments_df)} comments from JSON")
                return
            
            # Fallback: try CSV (for local development)
            possible_paths = [
                '/Users/eos/Documents/tik tok extraction/Presupuesto 2026/comment_data/Final Classification/comments_classified_ml_v3_current.csv',
                'comment_data/Final Classification/comments_classified_ml_v3_current.csv',
                '../../../comment_data/Final Classification/comments_classified_ml_v3_current.csv'
            ]
            
            for path in possible_paths:
                if os.path.exists(path):
                    import pandas as pd
                    self.comments_df = pd.read_csv(path, encoding='utf-8-sig')
                    print(f"Loaded {len(self.comments_df)} comments from CSV")
                    return
            
            print("Warning: Could not load comments data, using static examples only")
        except Exception as e:
            print(f"Error loading comments data: {e}")
            import traceback
            traceback.print_exc()
            self.comments_df = None
    
    def search_comments_dynamic(
        self,
        keywords: List[str],
        sentiment: str = None,
        max_results: int = 10
    ) -> Dict[str, Any]:
        """
        Dynamically search comments by keywords
        
        Args:
            keywords: List of keywords to search for
            sentiment: Filter by sentiment (optional)
            max_results: Maximum examples to return
            
        Returns:
            Dictionary with statistics and examples
        """
        if self.comments_df is None:
            return None
        
        try:
            import pandas as pd
            
            # Build regex pattern
            pattern = '|'.join(keywords)
            
            # Search in comment_text
            mask = self.comments_df['comment_text'].str.lower().str.contains(
                pattern, na=False, regex=True, case=False
            )
            matches = self.comments_df[mask]
            
            if len(matches) == 0:
                return None
            
            # Filter by sentiment if specified
            if sentiment:
                matches = matches[matches['predicted_sentiment_ml_v3'] == sentiment]
            
            # Calculate statistics
            total = len(matches)
            sentiment_counts = matches['predicted_sentiment_ml_v3'].value_counts().to_dict()
            
            stats = {
                'total': total,
                'negative': sentiment_counts.get('negative', 0),
                'positive': sentiment_counts.get('positive', 0),
                'neutral': sentiment_counts.get('neutral', 0),
                'pct_negative': round(sentiment_counts.get('negative', 0) / total * 100, 1) if total > 0 else 0,
                'pct_positive': round(sentiment_counts.get('positive', 0) / total * 100, 1) if total > 0 else 0,
                'pct_neutral': round(sentiment_counts.get('neutral', 0) / total * 100, 1) if total > 0 else 0
            }
            
            # Get examples
            examples = []
            for _, row in matches.head(max_results).iterrows():
                examples.append({
                    'text': row['comment_text'],
                    'sentiment': row['predicted_sentiment_ml_v3']
                })
            
            return {
                'stats': stats,
                'examples': examples,
                'keywords': keywords
            }
            
        except Exception as e:
            print(f"Error in dynamic search: {e}")
            return None
    
    # find_comments() method REMOVED - was returning fabricated static examples
    # All comment retrieval now goes through search_comments_dynamic() which uses real data
    
    def get_topic_stats(self, topic_key: str) -> Dict[str, Any]:
        """
        Get statistics for a specific topic
        
        Args:
            topic_key: Topic identifier (e.g., 'salud', 'educacion')
            
        Returns:
            Dictionary with statistics or None if not found
        """
        # Normalize topic key
        topic_key = topic_key.lower()
        if topic_key in self.topic_map:
            topic_key = self.topic_map[topic_key]
        
        return self.TOPIC_STATS.get(topic_key)
    
    def detect_topic_from_query(self, query: str) -> str:
        """
        Detect topic from user query
        
        Args:
            query: User's question
            
        Returns:
            Topic key or None
        """
        query_lower = query.lower()
        
        # Check each keyword in topic_map
        for keyword, topic in self.topic_map.items():
            if keyword in query_lower:
                return topic
        
        return None
    
    def get_comment_examples_context(self, query: str) -> str:
        """
        Generate context with real comment examples and statistics based on query
        
        Args:
            query: User's question
            
        Returns:
            Formatted string with statistics and comment examples
        """
        query_lower = query.lower()
        
        # Detect if user is asking for statistics/counts
        asking_for_stats = any(word in query_lower for word in [
            'cuanta', 'cuantos', 'cuantas', 'how many', 'porcentaje', 'percentage',
            'numero', 'number', 'cantidad', 'amount', 'estadistica', 'statistic'
        ])
        
        # Detect sentiment
        sentiment = None
        if any(word in query_lower for word in ['negativo', 'negative', 'crítico', 'malo', 'contra']):
            sentiment = 'negative'
        elif any(word in query_lower for word in ['positivo', 'positive', 'bueno', 'favor', 'apoyo']):
            sentiment = 'positive'
        elif any(word in query_lower for word in ['neutral', 'neutro']):
            sentiment = 'neutral'
        
        # Detect topic using the new method
        topic_key = self.detect_topic_from_query(query)
        
        # Build context
        context = "\n=== DATOS REALES DE COMENTARIOS ===\n\n"
        
        # Try dynamic search FIRST if comments data is available
        stats_found = False
        dynamic_result = None
        
        if self.comments_df is not None:
            # Extract potential keywords from query
            keywords = self._extract_keywords_from_query(query_lower)
            
            if keywords:
                dynamic_result = self.search_comments_dynamic(keywords, sentiment=None, max_results=8)
                
                if dynamic_result:
                    stats_found = True
                    stats = dynamic_result['stats']
                    
                    # Determine topic label for display
                    topic_label = topic_key.upper() if topic_key else ', '.join(keywords[:3])
                    
                    context += f"**Estadísticas sobre {topic_label}:**\n"
                    context += f"- Total de comentarios: {stats['total']}\n"
                    context += f"- Negativos: {stats['negative']} ({stats['pct_negative']}%)\n"
                    context += f"- Positivos: {stats['positive']} ({stats['pct_positive']}%)\n"
                    context += f"- Neutrales: {stats['neutral']} ({stats['pct_neutral']}%)\n\n"
                    
                    # Add examples
                    context += "**Ejemplos de comentarios reales:**\n\n"
                    for i, example in enumerate(dynamic_result['examples'], 1):
                        context += f"{i}. [{example['sentiment']}] \"{example['text']}\"\n"
                    context += "\n"
                    
                    context += "Fuente: Búsqueda dinámica en 2,042 comentarios extraídos de TikTok sobre Presupuesto 2026.\n"
                    return context
        
        # Fallback to static topics if dynamic search didn't work
        if not stats_found and topic_key:
            stats = self.get_topic_stats(topic_key)
            if stats:
                stats_found = True
                context += f"**Estadísticas sobre {topic_key.upper()}:**\n"
                context += f"- Total de comentarios: {stats['total']}\n"
                context += f"- Negativos: {stats['negative']} ({stats['pct_negative']}%)\n"
                context += f"- Positivos: {stats['positive']} ({stats['pct_positive']}%)\n"
                context += f"- Neutrales: {stats['neutral']} ({stats['pct_neutral']}%)\n\n"
                
                # If asking about positive sentiment specifically
                if sentiment == 'positive' or any(word in query_lower for word in ['mejor', 'mejora', 'mejorar']):
                    context += f"**RESPUESTA DIRECTA:** De los {stats['total']} comentarios sobre {topic_key}, "
                    context += f"solo {stats['positive']} ({stats['pct_positive']}%) expresan sentimiento positivo.\n\n"
        
        # If no keywords were found but user is asking for examples, return random samples
        if not stats_found and self.comments_df is not None:
            if any(word in query_lower for word in ['ejemplo', 'muestra', 'comentario', 'comment', 'show']):
                # Get random sample of comments (filtered by sentiment if specified)
                import pandas as pd
                
                sample_df = self.comments_df
                if sentiment:
                    sample_df = sample_df[sample_df['predicted_sentiment_ml_v3'] == sentiment]
                
                # Get random sample
                sample_comments = sample_df.sample(n=min(8, len(sample_df)))
                
                context += "**Ejemplos aleatorios de comentarios reales:**\n\n"
                for i, row in enumerate(sample_comments.itertuples(), 1):
                    context += f"{i}. [{row.predicted_sentiment_ml_v3}] \"{row.comment_text}\"\n"
                context += "\n"
                context += "Fuente: Muestra aleatoria de 2,042 comentarios extraídos de TikTok sobre Presupuesto 2026.\n"
                return context
        
        # If we reach here without finding data, return message explaining no examples available
        if not stats_found:
            if self.comments_df is None:
                context += "**NOTA**: No se pudieron cargar los comentarios. Sistema funcionando en modo limitado.\n"
            else:
                context += "**NOTA**: No se encontraron comentarios específicos para esta consulta.\n"
        
        if context.strip() == "=== DATOS REALES DE COMENTARIOS ===":
            # No content was added
            return ""
        
        context += "Fuente: Análisis de 2,042 comentarios extraídos de TikTok sobre Presupuesto 2026.\n"
        
        return context
    
    def _extract_keywords_from_query(self, query_lower: str) -> List[str]:
        """
        Extract relevant keywords from user query for dynamic search
        
        Args:
            query_lower: Lowercased user query
            
        Returns:
            List of keywords to search for
        """
        # Common topic keywords - expanded with more variations
        keyword_map = {
            'infraestructura': ['carretera', 'calle', 'camino', 'infraestructura', 'vial', 'puente', 'hoyo', 'bache'],
            'transporte': ['transporte', 'bus', 'camioneta', 'pasaje', 'movilidad'],
            'canasta': ['canasta', 'canasta basica', 'canasta básica'],
            'alimento': ['alimento', 'comida', 'alimentacion', 'alimentación'],
            'precio': ['precio', 'caro', 'costo', 'inflacion', 'inflación', 'costo de vida'],
            'salud': ['salud', 'hospital', 'medicina', 'medico', 'doctor', 'enfermera', 'clinica', 'igss'],
            'educacion': ['educacion', 'educación', 'escuela', 'maestro', 'profesor', 'estudiante', 'universidad'],
            'seguridad': ['seguridad', 'delincuencia', 'crimen', 'violencia', 'policia', 'policía', 'inseguridad'],
            'empleo': ['empleo', 'trabajo', 'desempleo', 'empleado', 'desocupacion', 'desocupación'],
            'vivienda': ['vivienda', 'casa', 'alquiler', 'renta', 'techo'],
            'corrupcion': ['corrup', 'robo', 'ladron', 'ladrón', 'roba', 'roban'],
            'impuesto': ['impuesto', 'sat', 'tax', 'fiscal'],
            'congreso': ['congreso', 'diputado', 'legisl', 'bancada'],
            'presidente': ['presidente', 'arevalo', 'arévalo', 'bernardo']
        }
        
        keywords = []
        for key, terms in keyword_map.items():
            for term in terms:
                if term in query_lower:
                    keywords.extend(terms)
                    break
        
        # Remove duplicates
        keywords = list(set(keywords))
        
        return keywords if keywords else []

