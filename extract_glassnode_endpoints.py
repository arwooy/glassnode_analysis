#!/usr/bin/env python3

import os
import re
import json
from typing import List, Dict, Any, Set


def process_all_files(docs_dir: str) -> Dict[str, Any]:
    """Process all HTML files and extract endpoints."""
    
    all_endpoints = {}
    category_stats = {}
    
    for filename in sorted(os.listdir(docs_dir)):
        if filename.endswith('.md'):  # Our files have .md extension but are HTML
            category = filename[:-3]
            file_path = os.path.join(docs_dir, filename)
            
            print(f"Processing {category}...")
            
            # Extract endpoints
            endpoints = extract_endpoints(file_path)
            
            if endpoints:
                # Try to enrich with additional info
                endpoints = extract_additional_info(file_path, endpoints)
                
                all_endpoints[category] = endpoints
                category_stats[category] = len(endpoints)
                print(f"  ✓ Found {len(endpoints)} unique endpoints")
            else:
                print(f"  ✗ No endpoints found")
    
    return all_endpoints, category_stats

def create_comprehensive_json(endpoints_by_category: Dict[str, List[Dict]]) -> Dict:
    """Create a comprehensive JSON structure with all endpoint information."""
    
    comprehensive = {
        'api': {
            'name': 'Glassnode API',
            'version': 'v1',
            'base_url': 'https://api.glassnode.com',
            'authentication': 'API key required',
            'rate_limits': 'Varies by tier'
        },
        'categories': {},
        'endpoints': []
    }
    
    # Organize by category
    for category, endpoints in endpoints_by_category.items():
        comprehensive['categories'][category] = {
            'name': category.replace('_', ' ').title(),
            'endpoint_count': len(endpoints),
            'endpoints': endpoints
        }
        
        # Also add to flat list
        for endpoint in endpoints:
            endpoint_copy = endpoint.copy()
            endpoint_copy['category'] = category
            comprehensive['endpoints'].append(endpoint_copy)
    
    # Add summary statistics
    comprehensive['summary'] = {
        'total_categories': len(comprehensive['categories']),
        'total_endpoints': len(comprehensive['endpoints']),
        'categories_list': list(comprehensive['categories'].keys())
    }
    
    return comprehensive

def main():
    docs_dir = "glassnode_docs"
    
    print("=" * 60)
    print("Glassnode API Endpoint Extractor")
    print("=" * 60)
    
    # Extract endpoints
    endpoints_by_category, stats = process_all_files(docs_dir)
    
    # Create comprehensive JSON
    comprehensive_data = create_comprehensive_json(endpoints_by_category)
    
    # Save main JSON file
    output_file = "glassnode_endpoints_complete.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(comprehensive_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n✓ Saved comprehensive endpoint data to {output_file}")
    
    # Save simplified flat version
    flat_file = "glassnode_endpoints_flat.json"
    with open(flat_file, 'w', encoding='utf-8') as f:
        json.dump(comprehensive_data['endpoints'], f, indent=2, ensure_ascii=False)
    
    print(f"✓ Saved flat endpoint list to {flat_file}")
    
    # Save category-only version
    categories_file = "glassnode_endpoints_by_category.json"
    with open(categories_file, 'w', encoding='utf-8') as f:
        json.dump(endpoints_by_category, f, indent=2, ensure_ascii=False)
    
    print(f"✓ Saved category-organized endpoints to {categories_file}")
    
    # Print summary
    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)
    print(f"Total categories: {comprehensive_data['summary']['total_categories']}")
    print(f"Total unique endpoints: {comprehensive_data['summary']['total_endpoints']}")
    print("\nEndpoints per category:")
    for category, count in sorted(stats.items(), key=lambda x: x[1], reverse=True):
        print(f"  {category:20} {count:4} endpoints")
    
    print("\n✓ Extraction complete!")

if __name__ == "__main__":
    main()