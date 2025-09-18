#!/usr/bin/env python3
"""
Create a final, comprehensive endpoints file by merging extracted JSON data
with the format suitable for glassnode_advanced_analysis.py
"""

import json
import os

def create_final_endpoints_config():
    """Create final endpoints configuration."""
    
    # Load the extracted JSON data
    with open('glassnode_endpoints_extracted.json', 'r') as f:
        extracted = json.load(f)
    
    # Create the final structure
    final = {
        'api': {
            'name': 'Glassnode API',
            'version': 'v1',
            'base_url': 'https://api.glassnode.com',
            'documentation': 'https://docs.glassnode.com/basic-api/endpoints',
            'authentication': 'API key required'
        },
        'categories': {},
        'summary': {
            'total_categories': len(extracted),
            'total_endpoints': sum(cat['endpoint_count'] for cat in extracted.values()),
            'extraction_date': '2025-09-18',
            'source': 'OpenAPI specifications from Glassnode documentation'
        }
    }
    
    # Process each category
    for category_name, category_data in extracted.items():
        category_entry = {
            'name': category_data['name'],
            'endpoint_count': category_data['endpoint_count'],
            'endpoints': []
        }
        
        # Process each endpoint
        for endpoint in category_data['endpoints']:
            endpoint_entry = {
                'metric': endpoint['metric'],
                'path': endpoint['path'],
                'method': endpoint.get('method', 'GET'),
                'summary': endpoint.get('summary', ''),
                'full_url': f"https://api.glassnode.com{endpoint['path']}"
            }
            
            # Add parameters if available
            if 'required_params' in endpoint:
                endpoint_entry['required_params'] = endpoint['required_params']
            if 'optional_params' in endpoint:
                endpoint_entry['optional_params'] = endpoint['optional_params']
            
            category_entry['endpoints'].append(endpoint_entry)
        
        final['categories'][category_name] = category_entry
    
    # Save the final configuration
    output_file = 'glassnode_endpoints_final.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(final, f, indent=2, ensure_ascii=False)
    
    print(f"✓ Created final endpoints configuration: {output_file}")
    
    # Also create a simplified version for glassnode_advanced_analysis.py
    simplified = {}
    for category_name, category_data in final['categories'].items():
        simplified[category_name] = {
            'name': category_data['name'],
            'endpoints': [
                {
                    'metric': ep['metric'],
                    'path': ep['path']
                }
                for ep in category_data['endpoints']
            ]
        }
    
    simplified_file = 'glassnode_endpoints_config_complete.json'
    with open(simplified_file, 'w', encoding='utf-8') as f:
        json.dump(simplified, f, indent=2, ensure_ascii=False)
    
    print(f"✓ Created simplified configuration: {simplified_file}")
    
    # Print summary
    print("\n" + "=" * 60)
    print("Final Endpoints Configuration Summary")
    print("=" * 60)
    print(f"Total categories: {final['summary']['total_categories']}")
    print(f"Total endpoints: {final['summary']['total_endpoints']}")
    print("\nTop 5 categories by endpoint count:")
    
    sorted_cats = sorted(
        final['categories'].items(), 
        key=lambda x: x[1]['endpoint_count'], 
        reverse=True
    )
    
    for cat_name, cat_data in sorted_cats[:5]:
        print(f"  {cat_name:<20} {cat_data['endpoint_count']:>4} endpoints")
    
    print("\n✓ Configuration files ready for use!")

if __name__ == "__main__":
    create_final_endpoints_config()