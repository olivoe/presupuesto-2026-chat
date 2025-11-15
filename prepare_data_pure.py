"""
Prepare comments data for chat app (Pure Python - no pandas)
Converts CSV to JSON with all necessary fields
"""

import csv
import json
import os

# Paths
CSV_PATH = '/Users/eos/Documents/tik tok extraction/Presupuesto 2026/comment_data/Final Classification/comments_classified_ml_v3_current.csv'
OUTPUT_PATH = '/Users/eos/Documents/tik tok extraction/Presupuesto 2026/chat_app/vercel/data/comments/comments_all.json'

print("="*80)
print("GENERATING comments_all.json FOR CHAT APP")
print("="*80)

print(f"\n1. Loading comments CSV: {CSV_PATH}")
comments = []

with open(CSV_PATH, 'r', encoding='utf-8-sig') as f:
    reader = csv.DictReader(f)
    
    for row in reader:
        comment_text = str(row.get('comment_text', '')).strip()
        
        # Skip empty or 'nan' comments
        if not comment_text or comment_text == 'nan':
            continue
        
        comment = {
            'text': comment_text,
            'sentiment': str(row.get('predicted_sentiment_ml_v3', 'neutral')).strip().lower(),
            'post_url': f"https://www.tiktok.com/@{row.get('username', 'unknown')}/video/{row.get('video_id', '')}",
            'post_stance': str(row.get('post_stance', 'N/A')).strip(),
            'author': str(row.get('commenter_username', 'N/A')).strip(),
            'likes': int(row.get('comment_likes', 0)) if row.get('comment_likes') and row.get('comment_likes') != '' else 0,
            'create_time': str(row.get('comment_created_time', 'N/A')).strip(),
            'confidence': float(row.get('confidence_ml_v3', 0.0)) if row.get('confidence_ml_v3') and row.get('confidence_ml_v3') != '' else 0.0
        }
        
        comments.append(comment)

print(f"   ✓ Loaded {len(comments)} valid comments")

# Show sentiment distribution
print(f"\n2. Sentiment distribution:")
sentiments = {}
for c in comments:
    s = c['sentiment']
    sentiments[s] = sentiments.get(s, 0) + 1

for sentiment, count in sorted(sentiments.items()):
    pct = count / len(comments) * 100 if comments else 0
    print(f"   {sentiment}: {count} ({pct:.1f}%)")

# Save to JSON
print(f"\n3. Saving to {OUTPUT_PATH}...")
os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
    json.dump(comments, f, ensure_ascii=False, indent=2)

print(f"   ✓ Saved {len(comments)} comments")

# Verify
print(f"\n4. Verification:")
print(f"   Expected: 1,580 comments")
print(f"   Actual: {len(comments)} comments")
print(f"   Match: {'✓ YES' if len(comments) == 1580 else '✗ NO'}")

# Show sample
print(f"\n5. Sample comments:")
for i, comment in enumerate(comments[:3], 1):
    text_preview = comment['text'][:80] + '...' if len(comment['text']) > 80 else comment['text']
    print(f"\n   {i}. [{comment['sentiment'].upper()}] {text_preview}")
    print(f"      Post: {comment['post_url']}")
    print(f"      Likes: {comment['likes']}")

print("\n" + "="*80)
print("GENERATION COMPLETE")
print("="*80)

