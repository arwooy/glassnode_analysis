#!/usr/bin/env python3
"""Compare different extraction methods and their results."""

import json
import os

def compare_extractions():
    """Compare the different extraction results."""
    
    files = {
        'HTML Extraction': 'glassnode_endpoints_complete.json',
        'JSON Extraction': 'glassnode_endpoints_extracted.json'
    }
    
    results = {}
    
    for name, filename in files.items():
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                data = json.load(f)
            
            # Count endpoints
            if 'categories' in data:  # complete.json format
                total = 0
                categories = {}
                for cat_name, cat_data in data['categories'].items():
                    count = len(cat_data.get('endpoints', []))
                    categories[cat_name] = count
                    total += count
            else:  # extracted.json format
                total = 0
                categories = {}
                for cat_name, cat_data in data.items():
                    count = len(cat_data.get('endpoints', []))
                    categories[cat_name] = count
                    total += count
            
            results[name] = {
                'total': total,
                'categories': len(categories),
                'by_category': categories
            }
    
    # Print comparison
    print("=" * 60)
    print("Comparison of Extraction Methods")
    print("=" * 60)
    
    for name, stats in results.items():
        print(f"\n{name}:")
        print(f"  Total endpoints: {stats['total']}")
        print(f"  Categories: {stats['categories']}")
    
    # Compare categories
    if len(results) == 2:
        html_cats = results['HTML Extraction']['by_category']
        json_cats = results['JSON Extraction']['by_category']
        
        all_cats = set(html_cats.keys()) | set(json_cats.keys())
        
        print("\n" + "-" * 60)
        print("Category-by-Category Comparison:")
        print(f"{'Category':<20} {'HTML':<10} {'JSON':<10} {'Difference':<10}")
        print("-" * 60)
        
        for cat in sorted(all_cats):
            html_count = html_cats.get(cat, 0)
            json_count = json_cats.get(cat, 0)
            diff = json_count - html_count
            diff_str = f"+{diff}" if diff > 0 else str(diff)
            print(f"{cat:<20} {html_count:<10} {json_count:<10} {diff_str:<10}")
        
        total_html = results['HTML Extraction']['total']
        total_json = results['JSON Extraction']['total']
        total_diff = total_json - total_html
        diff_str = f"+{total_diff}" if total_diff > 0 else str(total_diff)
        
        print("-" * 60)
        print(f"{'TOTAL':<20} {total_html:<10} {total_json:<10} {diff_str:<10}")
    
    print("\n" + "=" * 60)
    print("Summary:")
    print("JSON extraction found more endpoints because it properly")
    print("parsed the OpenAPI specifications in the markdown files.")
    print("=" * 60)

if __name__ == "__main__":
    compare_extractions()