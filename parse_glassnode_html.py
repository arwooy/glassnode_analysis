#!/usr/bin/env python3

import os
import re
import json
from bs4 import BeautifulSoup
from typing import List, Dict, Any

def extract_api_info_from_html(html_content: str) -> List[Dict[str, Any]]:
    """Extract API endpoint information from HTML documentation."""
    
    soup = BeautifulSoup(html_content, 'html.parser')
    endpoints = []
    
    # Find all code blocks
    code_blocks = soup.find_all('code')
    
    for block in code_blocks:
        text = block.get_text().strip()
        
        # Look for API endpoint patterns
        if '/v1/metrics/' in text or 'api.glassnode.com' in text:
            # This might be an endpoint
            endpoint_info = {
                'endpoint': text,
                'raw_text': text
            }
            
            # Try to find associated information
            parent = block.parent
            while parent and parent.name not in ['div', 'section', 'article']:
                parent = parent.parent
            
            if parent:
                # Look for tier information
                tier_match = re.search(r'Tier\s*(\d+)', parent.get_text(), re.IGNORECASE)
                if tier_match:
                    endpoint_info['tier'] = int(tier_match.group(1))
                
                # Look for resolution information
                res_text = parent.get_text()
                resolutions = []
                for res in ['10m', '1h', '24h', '1w', '1month']:
                    if res in res_text.lower():
                        resolutions.append(res)
                if resolutions:
                    endpoint_info['resolutions'] = resolutions
            
            endpoints.append(endpoint_info)
    
    # Also look for JSON blocks in script tags
    scripts = soup.find_all('script')
    for script in scripts:
        if script.string:
            # Look for JSON-like structures
            json_pattern = r'\{[^{}]*"endpoint"[^{}]*\}'
            matches = re.findall(json_pattern, script.string)
            for match in matches:
                try:
                    data = json.loads(match)
                    endpoints.append(data)
                except:
                    pass
    
    return endpoints

def parse_gitbook_html(html_file: str) -> Dict[str, Any]:
    """Parse GitBook HTML to extract structured API documentation."""
    
    with open(html_file, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Extract page title
    title = soup.find('title')
    page_title = title.get_text() if title else ""
    
    # Try to find the main content area
    main_content = soup.find('main') or soup.find('article') or soup.find('div', class_='content')
    
    result = {
        'title': page_title,
        'endpoints': []
    }
    
    if not main_content:
        # Fallback to searching the entire document
        main_content = soup
    
    # Look for endpoint information patterns
    # Pattern 1: Look for headers followed by code blocks
    headers = main_content.find_all(['h1', 'h2', 'h3', 'h4'])
    
    for header in headers:
        header_text = header.get_text().strip()
        
        # Look for the next code block after this header
        next_sibling = header.find_next_sibling()
        while next_sibling:
            if next_sibling.name == 'pre' or (next_sibling.name == 'div' and next_sibling.find('code')):
                code_elem = next_sibling.find('code') or next_sibling
                code_text = code_elem.get_text().strip()
                
                # Check if this looks like an API endpoint
                if '/v1/metrics/' in code_text or 'api.glassnode.com' in code_text:
                    endpoint_data = {
                        'name': header_text,
                        'endpoint': code_text,
                        'path': code_text.replace('https://api.glassnode.com', '')
                    }
                    
                    # Look for additional metadata
                    parent_section = header.parent
                    if parent_section:
                        section_text = parent_section.get_text()
                        
                        # Extract tier
                        tier_match = re.search(r'Tier\s*(\d+)', section_text, re.IGNORECASE)
                        if tier_match:
                            endpoint_data['tier'] = int(tier_match.group(1))
                        
                        # Extract resolutions
                        res_patterns = ['10m', '1h', '24h', '1w', '1month']
                        found_resolutions = []
                        for res in res_patterns:
                            if res in section_text.lower():
                                found_resolutions.append(res)
                        if found_resolutions:
                            endpoint_data['resolutions'] = found_resolutions
                        
                        # Extract assets/currencies
                        asset_patterns = ['BTC', 'ETH', 'LTC', 'USDT', 'USDC']
                        found_assets = []
                        for asset in asset_patterns:
                            if asset in section_text:
                                found_assets.append(asset)
                        if found_assets:
                            endpoint_data['assets'] = found_assets
                    
                    result['endpoints'].append(endpoint_data)
                    break
            
            next_sibling = next_sibling.find_next_sibling()
    
    # Pattern 2: Look for table rows with endpoint information
    tables = main_content.find_all('table')
    for table in tables:
        rows = table.find_all('tr')
        for row in rows:
            cells = row.find_all(['td', 'th'])
            if len(cells) >= 2:
                # Check if any cell contains an endpoint
                for cell in cells:
                    text = cell.get_text().strip()
                    if '/v1/metrics/' in text:
                        endpoint_data = {
                            'endpoint': text,
                            'path': text.replace('https://api.glassnode.com', '')
                        }
                        # Get other cells for context
                        for other_cell in cells:
                            if other_cell != cell:
                                other_text = other_cell.get_text().strip()
                                if 'tier' in other_text.lower():
                                    tier_match = re.search(r'(\d+)', other_text)
                                    if tier_match:
                                        endpoint_data['tier'] = int(tier_match.group(1))
                                elif any(res in other_text.lower() for res in ['10m', '1h', '24h']):
                                    endpoint_data['resolution_info'] = other_text
                        
                        result['endpoints'].append(endpoint_data)
    
    # Remove duplicates
    seen = set()
    unique_endpoints = []
    for ep in result['endpoints']:
        ep_key = ep.get('endpoint', ep.get('path', ''))
        if ep_key and ep_key not in seen:
            seen.add(ep_key)
            unique_endpoints.append(ep)
    
    result['endpoints'] = unique_endpoints
    
    return result

def process_all_html_files(docs_dir: str, output_file: str):
    """Process all HTML files and extract API information."""
    
    all_api_data = {
        'glassnode_api': {
            'base_url': 'https://api.glassnode.com',
            'categories': {}
        }
    }
    
    # Process each file
    for filename in sorted(os.listdir(docs_dir)):
        if filename.endswith('.md'):  # Our downloaded files have .md extension but are HTML
            category = filename[:-3]
            file_path = os.path.join(docs_dir, filename)
            
            print(f"Processing {category}...")
            
            try:
                result = parse_gitbook_html(file_path)
                
                if result['endpoints']:
                    print(f"  Found {len(result['endpoints'])} endpoints")
                    all_api_data['glassnode_api']['categories'][category] = result
                else:
                    print(f"  No endpoints found")
                    
            except Exception as e:
                print(f"  Error processing {category}: {e}")
    
    # Save the extracted data
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_api_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n✓ Saved extracted API data to {output_file}")
    
    # Create a flattened version
    flattened = []
    for category, data in all_api_data['glassnode_api']['categories'].items():
        for endpoint in data.get('endpoints', []):
            endpoint['category'] = category
            flattened.append(endpoint)
    
    flattened_file = output_file.replace('.json', '_flat.json')
    with open(flattened_file, 'w', encoding='utf-8') as f:
        json.dump(flattened, f, indent=2, ensure_ascii=False)
    
    print(f"✓ Saved flattened data to {flattened_file}")
    
    # Summary
    total_categories = len(all_api_data['glassnode_api']['categories'])
    total_endpoints = sum(
        len(data.get('endpoints', [])) 
        for data in all_api_data['glassnode_api']['categories'].values()
    )
    
    print(f"\nSummary:")
    print(f"  Categories: {total_categories}")
    print(f"  Total endpoints: {total_endpoints}")

def main():
    docs_dir = "glassnode_docs"
    output_file = "glassnode_api_extracted.json"
    
    print("=" * 60)
    print("Extracting API information from HTML files")
    print("=" * 60)
    
    process_all_html_files(docs_dir, output_file)
    
    print("\n" + "=" * 60)
    print("✓ Extraction completed!")
    print("=" * 60)

if __name__ == "__main__":
    main()