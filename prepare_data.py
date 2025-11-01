"""
Prepare comments data for smart filtering
Converts CSV to JSON with all necessary fields
"""

import pandas as pd
import json
import os

# Paths
CSV_PATH = '/Users/eos/Documents/tik tok extraction/Presupuesto 2026/comment_data/Final Classification/comments_classified_ml_v3_current.csv'
OUTPUT_PATH = '/Users/eos/Documents/tik tok extraction/Presupuesto 2026/chat_app/vercel/data/comments/comments_all.json'

print("Loading comments CSV...")
df = pd.read_csv(CSV_PATH, encoding='utf-8-sig')

print(f"Loaded {len(df)} comments")
print(f"Columns: {list(df.columns)}")

# Convert to list of dicts
comments = []
for idx, row in df.iterrows():
    comment = {
        'text': str(row.get('comment_text', '')).strip(),
        'sentiment': str(row.get('predicted_sentiment_ml_v3', 'neutral')).strip().lower(),
        'post_url': f"https://www.tiktok.com/@{row.get('username', 'unknown')}/video/{row.get('video_id', '')}",
        'post_stance': str(row.get('post_stance', 'N/A')).strip(),
        'author': str(row.get('commenter_username', 'N/A')).strip(),
        'likes': int(row.get('comment_likes', 0)) if pd.notna(row.get('comment_likes')) else 0,
        'create_time': str(row.get('comment_created_time', 'N/A')).strip(),
        'confidence': float(row.get('confidence_ml_v3', 0.0)) if pd.notna(row.get('confidence_ml_v3')) else 0.0
    }
    
    # Only add if text is not empty
    if comment['text'] and comment['text'] != 'nan' and len(comment['text']) > 2:
        comments.append(comment)

print(f"\nProcessed {len(comments)} valid comments")

# Show sentiment distribution
sentiments = {}
for c in comments:
    s = c['sentiment']
    sentiments[s] = sentiments.get(s, 0) + 1

print("\nSentiment distribution:")
for sentiment, count in sorted(sentiments.items()):
    pct = count / len(comments) * 100
    print(f"  {sentiment}: {count} ({pct:.1f}%)")

# Save to JSON
print(f"\nSaving to {OUTPUT_PATH}...")
os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
    json.dump(comments, f, ensure_ascii=False, indent=2)

print("✓ Done!")

# Show sample
print("\nSample comments:")
for i, comment in enumerate(comments[:3], 1):
    print(f"\n{i}. [{comment['sentiment'].upper()}] {comment['text'][:80]}...")
    print(f"   Post: {comment['post_url']}")
    print(f"   Likes: {comment['likes']}")

