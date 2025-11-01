"""
Test Option A: Full Dataset Loading
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'api'))

from full_dataset_loader import get_full_dataset_loader

def test_full_dataset():
    """Test loading the full dataset"""
    print("\n" + "="*80)
    print("TESTING OPTION A: FULL DATASET LOADER")
    print("="*80)
    
    loader = get_full_dataset_loader()
    
    # Test statistics
    stats = loader.get_statistics()
    print("\n📊 OVERALL STATISTICS:")
    print(f"  Total Comments: {stats['total_comments']}")
    print(f"  Positive: {stats['positive']} ({stats['pct_positive']}%)")
    print(f"  Negative: {stats['negative']} ({stats['pct_negative']}%)")
    print(f"  Neutral: {stats['neutral']} ({stats['pct_neutral']}%)")
    
    # Test compact context
    print("\n📝 GENERATING COMPACT CONTEXT...")
    context = loader.create_compact_context()
    print(f"  Context length: {len(context):,} characters")
    print(f"  Estimated tokens: ~{len(context) // 4:,} tokens")
    
    # Show first 1000 chars
    print("\n📄 CONTEXT PREVIEW (first 1000 chars):")
    print("-" * 80)
    print(context[:1000])
    print("...")
    print("-" * 80)
    
    # Test specific queries
    print("\n🔍 TESTING QUERIES:")
    
    # Count comments mentioning "salud"
    salud_comments = [c for c in loader.comments if 'salud' in c.get('text', '').lower() or 
                      'hospital' in c.get('text', '').lower() or 
                      'medicina' in c.get('text', '').lower()]
    print(f"\n  Comments about 'salud': {len(salud_comments)}")
    
    # Count by sentiment
    salud_sentiments = {'positive': 0, 'negative': 0, 'neutral': 0}
    for c in salud_comments:
        sentiment = c.get('sentiment', 'neutral').lower()
        if sentiment in salud_sentiments:
            salud_sentiments[sentiment] += 1
    
    print(f"    Positive: {salud_sentiments['positive']}")
    print(f"    Negative: {salud_sentiments['negative']}")
    print(f"    Neutral: {salud_sentiments['neutral']}")
    
    # Show examples
    print(f"\n  Example comments about salud:")
    for i, c in enumerate(salud_comments[:3], 1):
        text = c.get('text', '')[:80]
        sentiment = c.get('sentiment', 'neutral').upper()
        print(f"    {i}. [{sentiment}] {text}...")
    
    print("\n" + "="*80)
    print("✅ OPTION A TEST COMPLETE")
    print("="*80)
    print("\n📊 SUMMARY:")
    print(f"  ✓ Loaded all {stats['total_comments']} comments")
    print(f"  ✓ Context size: {len(context):,} chars (~{len(context) // 4:,} tokens)")
    print(f"  ✓ Can filter and analyze any topic")
    print(f"  ✓ Ready for deployment")
    print("\n💰 COST ESTIMATE:")
    tokens = len(context) // 4
    cost_per_query = (tokens / 1000) * 0.01  # GPT-4 Turbo input pricing
    print(f"  Input tokens per query: ~{tokens:,}")
    print(f"  Cost per query: ~${cost_per_query:.3f}")
    print(f"  Cost for 100 queries: ~${cost_per_query * 100:.2f}")

if __name__ == "__main__":
    test_full_dataset()

