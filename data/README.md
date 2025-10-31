# Presupuesto 2026 - Knowledge Base Data

This directory contains all the data files that power the AI Chat Assistant for the Presupuesto 2026 TikTok analysis project.

## 📊 **Data Overview**

**Total Size**: 408 KB  
**Last Updated**: October 31, 2025  
**Source**: TikTok posts and comments analysis

---

## 📁 **Directory Structure**

```
data/
├── comments/         # Comment-level data (2,042 comments)
├── posts/            # Post-level metadata (21 posts)
├── sentiment/        # Sentiment analysis aggregates
├── topics/           # Topic analysis results
└── reports/          # Final analysis reports
```

---

## 📄 **Data Files**

### **`comments/`** (231 KB)

#### `comments_all.json`
- **Size**: 231 KB
- **Records**: 2,042 comments
- **Fields**: 
  - `text`: Comment text
  - `sentiment`: Predicted sentiment (negative/positive/neutral)
- **Usage**: Dynamic comment search, examples, sentiment filtering

---

### **`posts/`** (33 KB)

#### `posts_metadata.json`
- **Size**: 20 KB
- **Records**: 21 posts
- **Fields**:
  - `video_id`: TikTok post ID
  - `username`: Account username
  - `post_url`: Full TikTok URL
  - `views`: View count
  - `likes`: Like count  
  - `comments`: Comment count
  - `shares`: Share count
  - `post_stance`: "approving" or "disapproving" of Presupuesto 2026
- **Usage**: Post queries, engagement metrics, stance analysis

#### `interest_index.json`
- **Size**: 13 KB
- **Records**: 21 entries
- **Fields**:
  - `video_id`: TikTok post ID
  - `username`: Account username
  - `interest_index`: Calculated Interest Index score
  - `historical_lift`: Lift vs. account's historical baseline
  - `relative_lift`: Lift vs. other posts in dataset
- **Usage**: Post ranking, Interest Index queries, performance comparison

---

### **`sentiment/`** (4 KB)

#### `sentiment_summary.json`
- **Size**: 440 B
- **Structure**:
  ```json
  {
    "overall": {
      "total_comments": 2042,
      "negative": 1957,
      "positive": 43,
      "neutral": 42,
      "pct_negative": 95.84,
      "pct_positive": 2.11,
      "pct_neutral": 2.06
    },
    "by_post_stance": {
      "approving": {...},
      "disapproving": {...}
    }
  }
  ```
- **Usage**: Overall sentiment stats, stance-based sentiment

#### `sentiment_by_topic.json`
- **Size**: 3.6 KB
- **Topics Tracked**: 13
  - salud, educacion, infraestructura, transporte, corrupcion, impuestos, pobreza, congreso, presidente, seguridad, empleo, vivienda, canasta_basica
- **Per Topic**:
  - `keywords`: List of detection keywords
  - `total`: Number of comments
  - `negative/positive/neutral`: Counts and percentages
- **Usage**: Topic-specific sentiment queries

---

### **`topics/`** (34 KB)

#### `topic_analysis.json`
- **Size**: 26 KB
- **Contains**:
  - TF-IDF distinctive keywords
  - LDA topics (Latent Dirichlet Allocation)
  - NMF components (Non-Negative Matrix Factorization)
- **Organized by**: negative, positive, neutral sentiment
- **Usage**: Topic extraction, keyword analysis

#### `psychosocial_insights.txt`
- **Size**: 7.7 KB
- **Contains**: Human expert analysis of comment themes
- **Topics**:
  - Desconfianza institucional profunda
  - Percepción de injusticia distributiva
  - Resignación y fatalismo
  - Crítica al establishment político
  - Demanda de transparencia
  - And more...
- **Usage**: Psychosocial context, theme interpretation

---

### **`reports/`** (90 KB)

#### `PRESUPUESTO_2026_ANALYSIS_REPORT_CURRENT.html`
- **Size**: 90 KB
- **Contains**:
  - Executive summary
  - Interest Index rankings
  - Sentiment analysis results
  - Weighted sentiment (likes-adjusted)
  - Bias-corrected estimates
  - Topic analysis
  - Psychosocial insights
  - Methodology
- **Usage**: Complete analysis reference, report queries

---

## 🔍 **Data Dictionary**

### **Sentiment Labels**
- `negative`: Critical, disapproving, or negative sentiment toward Presupuesto 2026
- `positive`: Supportive, approving, or positive sentiment
- `neutral`: Neither positive nor negative, or ambiguous

### **Post Stance**
- `approving`: Post expresses support for Presupuesto 2026
- `disapproving`: Post criticizes or opposes Presupuesto 2026

### **Interest Index**
- **Scale**: Normalized score (higher = more interest)
- **Components**:
  - Historical Lift: Performance vs. account's historical baseline
  - Relative Lift: Performance vs. other posts in dataset
- **Formula**: Geometric mean of time-normalized views with robust estimation

---

## 📈 **Key Statistics**

### **Comments**
- Total: 2,042
- Negative: 1,957 (95.84%)
- Positive: 43 (2.11%)
- Neutral: 42 (2.06%)

### **Posts**
- Total: 21
- Approving: 9
- Disapproving: 12

### **Topics Tracked**
- Total: 13 topics
- Most mentioned: Corrupción (275 comments, 96.4% negative)
- Least mentioned: Educación (20 comments, 90% negative)

### **Top Topics by Comment Count**
1. **Corrupción**: 275 comments (96.4% neg)
2. **Presidente**: 169 comments (96.4% neg)
3. **Congreso**: 106 comments (96.2% neg)
4. **Infraestructura**: 67 comments (98.5% neg)
5. **Salud**: 32 comments (84.4% neg)

---

## 🔄 **Update Frequency**

- **Comments**: Static (analysis complete)
- **Sentiment**: Static (models trained and frozen)
- **Reports**: May be updated if methodology improves

---

## 🛠️ **Usage in Code**

### **Load Comments**
```python
import json
with open('data/comments/comments_all.json', 'r', encoding='utf-8') as f:
    comments = json.load(f)
```

### **Load Sentiment by Topic**
```python
with open('data/sentiment/sentiment_by_topic.json', 'r', encoding='utf-8') as f:
    sentiment_by_topic = json.load(f)
    
# Get salud stats
salud_stats = sentiment_by_topic['salud']
print(f"Salud: {salud_stats['total']} comments, {salud_stats['pct_negative']}% negative")
```

### **Load Posts**
```python
with open('data/posts/posts_metadata.json', 'r', encoding='utf-8') as f:
    posts = json.load(f)
```

---

## 📝 **Data Lineage**

### **Source Files** (from parent project)
- `comment_data/Final Classification/comments_classified_ml_v3_current.csv`
- `presupuesto_2026_posts_current.csv`
- `interest_index_results_current.csv`
- `comment_data/Final Classification/Topic analysis/topic_analysis_results_current.json`
- `comment_data/Final Classification/PRESUPUESTO_2026_ANALYSIS_REPORT_CURRENT.html`

### **Processing**
- Comments: Converted CSV → JSON, kept only text + sentiment
- Sentiment by Topic: Calculated from comments using keyword matching
- Posts/Interest Index: Direct JSON conversion from CSV

---

## ⚠️ **Important Notes**

1. **Encoding**: All files use UTF-8 encoding to handle Spanish characters and emojis
2. **Size Optimization**: Comments JSON is compact (text + sentiment only) to fit Vercel limits
3. **Immutability**: This data represents a snapshot of the analysis - not real-time
4. **Privacy**: All data is from public TikTok posts

---

## 📊 **Data Quality**

- **Comments Extraction**: ~85% extraction rate (limited by TikTok API)
- **Sentiment Accuracy**: 
  - Model A (approving posts): 73.1% accuracy
  - Model B (disapproving posts): 76.0% accuracy
- **Bias Correction**: Applied Missing Data CI Inflation method
- **Topic Detection**: Keyword-based matching (100% precision, variable recall)

---

## 🔗 **Related Files**

- **API Modules**: `/api/comment_retrieval.py`, `/api/post_retrieval.py`, `/api/topic_retrieval.py`
- **Proposal**: `/KNOWLEDGE_BASE_PROPOSAL.md`
- **Deployment**: `/VERCEL_DEPLOYMENT.md`

---

**Generated**: October 31, 2025  
**Project**: Presupuesto 2026 TikTok Analysis  
**Version**: 1.0

