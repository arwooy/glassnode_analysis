# Glassnode API Endpoints Extraction

## Overview
Successfully extracted **619 unique API endpoints** from Glassnode documentation across **21 categories**.

## Files Generated

1. **`glassnode_endpoints_complete.json`** - Complete structured data with all metadata
   - Organized by categories
   - Includes API base URL and authentication info
   - Full endpoint paths and URLs

2. **`glassnode_endpoints_flat.json`** - Flattened list of all endpoints
   - Simple array format
   - Each endpoint includes its category

3. **`glassnode_endpoints_by_category.json`** - Endpoints organized by category
   - Dictionary structure with category as key
   - Easy to navigate specific categories

## Categories & Endpoint Count

| Category | Endpoints |
|----------|-----------|
| indicators | 126 |
| transactions | 103 |
| derivatives | 54 |
| supply | 47 |
| distribution | 45 |
| breakdowns | 42 |
| protocols | 30 |
| addresses | 29 |
| market | 28 |
| fees | 27 |
| blockchain | 18 |
| mining | 12 |
| entities | 11 |
| signals | 11 |
| lightning | 10 |
| mempool | 10 |
| institutions | 7 |
| bridges | 5 |
| options | 2 |
| defi | 1 |
| eth2 | 1 |

## Usage

```python
import json

# Load complete data
with open('glassnode_endpoints_complete.json', 'r') as f:
    data = json.load(f)

# Access specific category
addresses_endpoints = data['categories']['addresses']['endpoints']

# Get all endpoints as flat list
all_endpoints = data['endpoints']
```

## Scripts

- **`download_glassnode_docs_v2.py`** - Downloads HTML documentation from Glassnode
- **`extract_glassnode_endpoints.py`** - Extracts and structures endpoint information
- **`parse_glassnode_html.py`** - Alternative HTML parser (for reference)

## Downloaded Documentation

All raw HTML documentation is stored in the `glassnode_docs/` directory.