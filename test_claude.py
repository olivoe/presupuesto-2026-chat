"""
Test Claude Haiku 3.5 integration
"""

import os
import sys

# Set API key from environment (set before running: export ANTHROPIC_API_KEY=your_key)
if 'ANTHROPIC_API_KEY' not in os.environ:
    print("ERROR: ANTHROPIC_API_KEY environment variable not set")
    print("Run: export ANTHROPIC_API_KEY=your_key")
    sys.exit(1)

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'api'))

from full_dataset_loader import get_full_dataset_loader
import anthropic

def test_claude():
    """Test Claude with full dataset"""
    print("\n" + "="*80)
    print("TESTING CLAUDE HAIKU 3.5 WITH FULL DATASET")
    print("="*80)
    
    # Load dataset
    print("\n📊 Loading dataset...")
    loader = get_full_dataset_loader()
    context = loader.create_compact_context()
    
    print(f"  Dataset size: {len(context):,} characters")
    print(f"  Estimated tokens: ~{len(context) // 4:,}")
    
    # Test query
    test_query = "Qué piensa la gente sobre carreteras?"
    
    print(f"\n🧪 Test query: \"{test_query}\"")
    print("\n📤 Sending to Claude...")
    
    # Build prompts
    system_prompt = """You are an expert analyzing TikTok comments about Guatemala's 2026 budget.
You have access to ALL 2,042 comments in ultra-compact format.
Provide accurate statistics and real comment examples."""
    
    user_prompt = context + f"\n\nUSER QUERY: {test_query}"
    
    # Call Claude
    try:
        client = anthropic.Anthropic(api_key=os.environ['ANTHROPIC_API_KEY'])
        
        message = client.messages.create(
            model="claude-3-5-haiku-20241022",
            max_tokens=1000,
            temperature=0.7,
            system=system_prompt,
            messages=[
                {"role": "user", "content": user_prompt}
            ]
        )
        
        response = message.content[0].text
        
        print("\n📥 Claude Response:")
        print("-" * 80)
        print(response)
        print("-" * 80)
        
        print("\n✅ TEST SUCCESSFUL!")
        print(f"  Input tokens: ~{len(user_prompt) // 4:,}")
        print(f"  Output tokens: ~{len(response) // 4:,}")
        print(f"  Total cost: ~${((len(user_prompt) // 4) * 0.80 + (len(response) // 4) * 4) / 1_000_000:.4f}")
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "="*80)

if __name__ == "__main__":
    test_claude()

