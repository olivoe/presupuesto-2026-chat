"""
Test the smart filter system locally
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'api'))

from smart_filter import get_smart_filter

def test_query(query: str):
    """Test a query with the smart filter"""
    print("\n" + "="*80)
    print(f"QUERY: {query}")
    print("="*80)
    
    smart_filter = get_smart_filter()
    context = smart_filter.create_context_for_llm(query)
    
    print(context)
    print("\n" + "="*80)
    print(f"Context length: {len(context)} characters")
    print("="*80)

# Test queries
test_queries = [
    "Qué piensa la gente sobre carreteras y transporte?",
    "Dame ejemplos de comentarios sobre salud",
    "Cuánta gente piensa que habrá mejor servicio de salud?",
    "Muestrame comentarios sobre diputados y el Congreso",
    "Qué dicen sobre los precios de la canasta básica?",
    "Comentarios sobre corrupción"
]

print("\n🧪 TESTING SMART FILTER SYSTEM (Option B)")
print("="*80)

for query in test_queries:
    test_query(query)
    input("\nPress Enter to continue to next test...")

print("\n✅ All tests complete!")

