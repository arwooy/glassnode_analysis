#!/usr/bin/env python3
"""
Extract JSON OpenAPI specifications from Glassnode documentation MD files
and generate a structured endpoints configuration file.
"""

import os
import re
import json
from typing import List, Dict, Any

def extract_json_blocks_from_md(md_file: str) -> List[Dict[str, Any]]:
    """Extract all JSON blocks from a markdown file."""
    with open(md_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find all JSON code blocks (between ```json and ```)
    json_pattern = r'```json\s*(.*?)\s*```'
    json_blocks = re.findall(json_pattern, content, re.DOTALL)
    
    extracted_jsons = []
    for block in json_blocks:
        try:
            # Parse the JSON
            json_data = json.loads(block)
            extracted_jsons.append(json_data)
        except json.JSONDecodeError as e:
            # Try to fix common issues
            try:
                # Remove trailing commas
                fixed_block = re.sub(r',\s*}', '}', block)
                fixed_block = re.sub(r',\s*]', ']', fixed_block)
                json_data = json.loads(fixed_block)
                extracted_jsons.append(json_data)
            except:
                print(f"  Warning: Could not parse JSON block: {str(e)[:50]}")
    
    return extracted_jsons

def extract_endpoint_info(openapi_spec: Dict) -> Dict[str, Any]:
    """Extract endpoint information from OpenAPI specification."""
    endpoint_info = {}
    
    # Get basic info
    if 'info' in openapi_spec:
        endpoint_info['title'] = openapi_spec['info'].get('title', '')
        endpoint_info['version'] = openapi_spec['info'].get('version', '')
    
    # Get server info
    if 'servers' in openapi_spec and openapi_spec['servers']:
        endpoint_info['base_url'] = openapi_spec['servers'][0].get('url', '')
    
    # Extract paths (endpoints)
    endpoints = []
    if 'paths' in openapi_spec:
        for path, methods in openapi_spec['paths'].items():
            for method, details in methods.items():
                if method in ['get', 'post', 'put', 'delete']:
                    endpoint = {
                        'path': path,
                        'method': method.upper(),
                        'summary': details.get('summary', ''),
                        'description': details.get('description', ''),
                        'operationId': details.get('operationId', ''),
                        'parameters': []
                    }
                    
                    # Extract parameters
                    if 'parameters' in details:
                        for param in details['parameters']:
                            param_info = {
                                'name': param.get('name', ''),
                                'in': param.get('in', ''),
                                'required': param.get('required', False),
                                'description': param.get('description', ''),
                                'type': param.get('schema', {}).get('type', '') if 'schema' in param else ''
                            }
                            endpoint['parameters'].append(param_info)
                    
                    # Extract metric name from path
                    path_parts = path.strip('/').split('/')
                    if len(path_parts) >= 4:  # e.g., v1/metrics/addresses/active_count
                        endpoint['category'] = path_parts[2]
                        endpoint['metric'] = path_parts[3] if len(path_parts) > 3 else ''
                    
                    endpoints.append(endpoint)
    
    endpoint_info['endpoints'] = endpoints
    return endpoint_info

def process_all_md_files(docs_dir: str) -> Dict[str, List[Dict]]:
    """Process all MD files and extract endpoint information."""
    all_endpoints_by_category = {}
    
    for filename in sorted(os.listdir(docs_dir)):
        if filename.endswith('.md'):
            category = filename[:-3]  # Remove .md extension
            file_path = os.path.join(docs_dir, filename)
            
            print(f"\nProcessing {filename}...")
            
            # Extract JSON blocks
            json_blocks = extract_json_blocks_from_md(file_path)
            print(f"  Found {len(json_blocks)} JSON blocks")
            
            if json_blocks:
                category_endpoints = []
                
                for json_block in json_blocks:
                    # Check if this is an OpenAPI spec
                    if 'openapi' in json_block and 'paths' in json_block:
                        endpoint_info = extract_endpoint_info(json_block)
                        
                        # Add all endpoints from this spec
                        for endpoint in endpoint_info.get('endpoints', []):
                            # Ensure category matches
                            if 'category' not in endpoint or not endpoint['category']:
                                endpoint['category'] = category
                            
                            # Create a simplified endpoint entry
                            simplified = {
                                'path': endpoint['path'],
                                'method': endpoint['method'],
                                'metric': endpoint.get('metric', ''),
                                'summary': endpoint.get('summary', ''),
                                'description': endpoint.get('description', '')[:200] if endpoint.get('description') else '',
                                'parameters': endpoint.get('parameters', [])
                            }
                            
                            # Check for supported assets
                            if 'Supported asset ids:' in endpoint.get('description', ''):
                                desc_parts = endpoint['description'].split('Supported asset ids:')
                                if len(desc_parts) > 1:
                                    assets = desc_parts[1].strip().split(',')[:10]  # First 10 assets
                                    simplified['sample_assets'] = [a.strip() for a in assets]
                            
                            category_endpoints.append(simplified)
                
                if category_endpoints:
                    # Remove duplicates based on path
                    unique_endpoints = {}
                    for ep in category_endpoints:
                        unique_endpoints[ep['path']] = ep
                    
                    all_endpoints_by_category[category] = list(unique_endpoints.values())
                    print(f"  ✓ Extracted {len(unique_endpoints)} unique endpoints")
            else:
                print(f"  ✗ No valid OpenAPI specs found")
    
    return all_endpoints_by_category

def create_structured_output(endpoints_by_category: Dict[str, List[Dict]]) -> Dict:
    """Create a structured output similar to glassnode_endpoints_by_category.json."""
    structured = {}
    
    for category, endpoints in endpoints_by_category.items():
        # Sort endpoints by path
        sorted_endpoints = sorted(endpoints, key=lambda x: x['path'])
        
        # Create category entry
        structured[category] = {
            'name': category.replace('_', ' ').title(),
            'endpoint_count': len(sorted_endpoints),
            'endpoints': []
        }
        
        # Add simplified endpoint info
        for endpoint in sorted_endpoints:
            # Extract just the metric name from path
            path_parts = endpoint['path'].strip('/').split('/')
            metric_name = path_parts[-1] if path_parts else ''
            
            endpoint_entry = {
                'metric': metric_name,
                'path': endpoint['path'],
                'method': endpoint['method'],
                'summary': endpoint['summary']
            }
            
            # Add optional fields if present
            if 'sample_assets' in endpoint:
                endpoint_entry['sample_assets'] = endpoint['sample_assets']
            
            # Add key parameters
            params = endpoint.get('parameters', [])
            required_params = [p['name'] for p in params if p.get('required')]
            optional_params = [p['name'] for p in params if not p.get('required')]
            
            if required_params:
                endpoint_entry['required_params'] = required_params
            if optional_params:
                endpoint_entry['optional_params'] = optional_params[:5]  # Limit to first 5
            
            structured[category]['endpoints'].append(endpoint_entry)
    
    return structured

def main():
    docs_dir = "glassnode_docs"
    output_file = "glassnode_endpoints_extracted.json"
    output_file_detailed = "glassnode_endpoints_detailed.json"
    
    print("=" * 60)
    print("Extracting JSON from Glassnode Documentation")
    print("=" * 60)
    
    # Process all MD files
    endpoints_by_category = process_all_md_files(docs_dir)
    
    # Create structured output
    structured_data = create_structured_output(endpoints_by_category)
    
    # Save structured data
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(structured_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n✓ Saved structured endpoints to {output_file}")
    
    # Also save detailed version with all extracted data
    with open(output_file_detailed, 'w', encoding='utf-8') as f:
        json.dump(endpoints_by_category, f, indent=2, ensure_ascii=False)
    
    print(f"✓ Saved detailed endpoints to {output_file_detailed}")
    
    # Print summary
    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)
    
    total_endpoints = sum(len(cat['endpoints']) for cat in structured_data.values())
    print(f"Total categories: {len(structured_data)}")
    print(f"Total endpoints: {total_endpoints}")
    
    print("\nEndpoints per category:")
    for category, data in sorted(structured_data.items(), key=lambda x: len(x[1]['endpoints']), reverse=True):
        print(f"  {category:20} {len(data['endpoints']):4} endpoints")
    
    print("\n✓ Extraction complete!")

if __name__ == "__main__":
    main()