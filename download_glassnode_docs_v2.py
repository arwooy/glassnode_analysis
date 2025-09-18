#!/usr/bin/env python3

import os
import re
import json
import time
import requests
from typing import List, Dict, Any

# Known Glassnode endpoint categories based on their documentation
GLASSNODE_CATEGORIES = [
    'addresses',
    'bridges',
    'blockchain',
    'breakdowns',
    'defi',
    'derivatives',
    'distribution',
    'entities',
    'eth2',
    'fees',
    'indicators',
    'institutions',
    'lightning',
    'market',
    'mempool',
    'mining',
    'options',
    'point-in-time',
    'protocols',
    'signals',
    'supply',
    'transactions'
]

def download_endpoint_documentation(category: str, output_dir: str) -> bool:
    """Download endpoint documentation for a specific category."""
    
    # Construct the documentation URL
    base_url = f"https://docs.glassnode.com/basic-api/endpoints/{category}.md"
    
    # Try to fetch the page content directly
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    }
    
    print(f"Fetching {category}...")
    
    try:
        # First try to get the HTML page
        response = requests.get(base_url, headers=headers)
        
        if response.status_code == 200:
            # Save as markdown-like format
            output_path = os.path.join(output_dir, f"{category}.md")
            
            # Extract content (the response might already contain structured data)
            content = response.text
            
            # Save the content
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"  ✓ Saved {category}.md ({len(content)} bytes)")
            return True
        else:
            print(f"  ✗ Failed to fetch {category} (status: {response.status_code})")
            
    except Exception as e:
        print(f"  ✗ Error fetching {category}: {e}")
    
    return False

def extract_json_blocks(file_path: str) -> List[Dict[str, Any]]:
    """Extract all JSON blocks from a file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    extracted_data = []
    
    # Method 1: Find JSON code blocks in markdown
    json_pattern = r'```json\s*(.*?)\s*```'
    json_blocks = re.findall(json_pattern, content, re.DOTALL)
    
    for block in json_blocks:
        try:
            json_data = json.loads(block)
            extracted_data.append(json_data)
        except json.JSONDecodeError:
            # Try to fix common JSON issues
            try:
                # Remove trailing commas
                fixed = re.sub(r',\s*([}\]])', r'\1', block)
                # Remove comments if any
                fixed = re.sub(r'//.*$', '', fixed, flags=re.MULTILINE)
                json_data = json.loads(fixed)
                extracted_data.append(json_data)
            except:
                pass
    
    # Method 2: Try to find JSON-like structures in the content
    if not extracted_data:
        # Look for objects starting with { and ending with }
        json_pattern2 = r'(\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\})'
        potential_jsons = re.findall(json_pattern2, content)
        
        for potential in potential_jsons:
            try:
                json_data = json.loads(potential)
                # Only add if it looks like endpoint data
                if any(key in str(json_data).lower() for key in ['endpoint', 'path', 'url', 'metric', 'address']):
                    extracted_data.append(json_data)
            except:
                pass
    
    return extracted_data

def create_endpoint_structure(category: str, json_blocks: List[Dict]) -> Dict:
    """Create a structured endpoint entry from extracted JSON blocks."""
    
    # Try to identify different types of data in the JSON blocks
    endpoints = []
    metadata = {}
    
    for block in json_blocks:
        # Check if this looks like an endpoint definition
        if isinstance(block, dict):
            if 'path' in block or 'endpoint' in block or 'url' in block:
                endpoints.append(block)
            elif 'tier' in block or 'resolutions' in block or 'formats' in block:
                metadata.update(block)
            else:
                # Could be example data or response
                if not metadata.get('example'):
                    metadata['example'] = block
    
    return {
        'category': category,
        'endpoints': endpoints if endpoints else json_blocks,
        'metadata': metadata if metadata else None
    }

def merge_all_endpoints(docs_dir: str, output_file: str):
    """Process all downloaded files and merge into a single JSON."""
    
    all_data = {
        'glassnode_api': {
            'version': 'v1',
            'base_url': 'https://api.glassnode.com',
            'categories': {}
        }
    }
    
    # Process each markdown file
    for filename in sorted(os.listdir(docs_dir)):
        if filename.endswith('.md'):
            category = filename[:-3]
            file_path = os.path.join(docs_dir, filename)
            
            print(f"\nProcessing {category}...")
            
            # Extract JSON blocks
            json_blocks = extract_json_blocks(file_path)
            
            if json_blocks:
                print(f"  Found {len(json_blocks)} JSON blocks")
                
                # Structure the data
                structured_data = create_endpoint_structure(category, json_blocks)
                all_data['glassnode_api']['categories'][category] = structured_data
            else:
                print(f"  No JSON blocks found")
                # Still add the category with empty data
                all_data['glassnode_api']['categories'][category] = {
                    'category': category,
                    'endpoints': [],
                    'metadata': None
                }
    
    # Save the merged data
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_data, f, indent=2, ensure_ascii=False)
    
    # Create a flattened version for easier access
    flattened_file = output_file.replace('.json', '_flat.json')
    flattened_data = []
    
    for category, data in all_data['glassnode_api']['categories'].items():
        for endpoint in data.get('endpoints', []):
            if isinstance(endpoint, dict):
                endpoint['category'] = category
                flattened_data.append(endpoint)
    
    with open(flattened_file, 'w', encoding='utf-8') as f:
        json.dump(flattened_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n✓ Saved structured data to {output_file}")
    print(f"✓ Saved flattened data to {flattened_file}")
    
    # Print summary
    total_categories = len(all_data['glassnode_api']['categories'])
    total_endpoints = sum(
        len(data.get('endpoints', [])) 
        for data in all_data['glassnode_api']['categories'].values()
    )
    
    print(f"\nSummary:")
    print(f"  Categories processed: {total_categories}")
    print(f"  Total endpoints found: {total_endpoints}")

def main():
    # Configuration
    output_dir = "glassnode_docs"
    merged_json_file = "glassnode_api_endpoints.json"
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    print("=" * 60)
    print("Glassnode API Documentation Downloader")
    print("=" * 60)
    
    # Step 1: Download all category documentation
    print("\nStep 1: Downloading endpoint documentation")
    print("-" * 40)
    
    successful = 0
    for i, category in enumerate(GLASSNODE_CATEGORIES, 1):
        print(f"\n[{i}/{len(GLASSNODE_CATEGORIES)}] {category}")
        
        if download_endpoint_documentation(category, output_dir):
            successful += 1
            time.sleep(0.5)  # Be polite to the server
    
    print(f"\n✓ Downloaded {successful}/{len(GLASSNODE_CATEGORIES)} categories")
    
    # Step 2: Extract and merge JSON data
    print("\n" + "=" * 60)
    print("Step 2: Extracting and merging JSON data")
    print("-" * 40)
    
    merge_all_endpoints(output_dir, merged_json_file)
    
    print("\n" + "=" * 60)
    print("✓ Process completed!")
    print("=" * 60)

if __name__ == "__main__":
    main()