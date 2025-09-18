# Glassnode JSON Extraction Summary

## Overview
Successfully extracted **734 API endpoints** from OpenAPI specifications embedded in Glassnode documentation MD files.

## Process

1. **Downloaded Documentation**: HTML files from Glassnode docs (stored as .md files)
2. **Extracted JSON**: Found OpenAPI 3.0.3 specifications within markdown code blocks
3. **Parsed Specifications**: Extracted endpoint paths, methods, parameters, and descriptions
4. **Generated Configurations**: Created multiple output formats for different use cases

## Files Generated

### Primary Output Files

1. **`glassnode_endpoints_final.json`** (734 endpoints)
   - Complete endpoint information with all metadata
   - Includes parameters, summaries, and full URLs
   - Organized by category with detailed structure

2. **`glassnode_endpoints_extracted.json`** (734 endpoints)
   - Direct extraction from OpenAPI specs
   - Includes required/optional parameters
   - Category-based organization

3. **`glassnode_endpoints_config_complete.json`** (734 endpoints)
   - Simplified format for `glassnode_advanced_analysis.py`
   - Contains metric names and paths
   - Optimized for API calls

### Comparison with HTML Extraction

| Method | Endpoints | Source |
|--------|-----------|--------|
| HTML Pattern Extraction | 619 | Regex patterns in HTML |
| JSON OpenAPI Extraction | 734 | OpenAPI specifications |

**Improvement: +115 endpoints (18.6% increase)**

## Categories & Endpoint Distribution

| Category | Endpoints | Description |
|----------|-----------|-------------|
| indicators | 158 | Technical indicators and metrics |
| transactions | 94 | Transaction analytics |
| supply | 61 | Supply metrics |
| derivatives | 58 | Derivatives data |
| protocols | 58 | Protocol-specific metrics |
| addresses | 50 | Address analytics |
| distribution | 42 | Distribution metrics |
| breakdowns | 39 | Detailed breakdowns |
| market | 32 | Market data |
| fees | 28 | Fee analytics |
| eth2 | 22 | Ethereum 2.0 metrics |
| blockchain | 18 | Blockchain metrics |
| entities | 18 | Entity analytics |
| signals | 14 | Trading signals |
| lightning | 10 | Lightning Network |
| mempool | 10 | Mempool analytics |
| mining | 9 | Mining metrics |
| institutions | 7 | Institutional data |
| bridges | 5 | Bridge metrics |
| defi | 1 | DeFi metrics |

## Key Features Extracted

Each endpoint includes:
- **Path**: Full API path (e.g., `/v1/metrics/addresses/active_count`)
- **Method**: HTTP method (GET)
- **Summary**: Brief description
- **Parameters**:
  - Required: Typically `a` (asset)
  - Optional: `s` (since), `u` (until), `i` (interval), `f` (format), etc.
- **Full URL**: Complete API endpoint URL

## Usage

### With glassnode_advanced_analysis.py

The script now automatically uses `glassnode_endpoints_final.json` or `glassnode_endpoints_config_complete.json`:

```python
analyzer = GlassnodeAdvancedAnalyzer(api_key)
# Automatically loads 734 endpoints with proper paths
```

### Direct API Calls

```python
import json

with open('glassnode_endpoints_final.json', 'r') as f:
    config = json.load(f)

# Access specific endpoint
addresses = config['categories']['addresses']['endpoints']
for endpoint in addresses:
    url = endpoint['full_url']
    params = {
        'a': 'BTC',
        **{p: value for p in endpoint.get('optional_params', [])}
    }
```

## Benefits

1. **Complete Coverage**: All documented Glassnode API endpoints
2. **Accurate Paths**: Directly from OpenAPI specifications
3. **Parameter Information**: Know which parameters are required/optional
4. **Structured Data**: Multiple formats for different use cases
5. **Ready for Analysis**: Works directly with the analysis scripts

## Scripts

- `extract_json_from_docs.py`: Main extraction script
- `create_final_endpoints.py`: Creates final configurations
- `compare_extractions.py`: Compares extraction methods

## Next Steps

1. Use `glassnode_endpoints_final.json` for comprehensive API access
2. Run `glassnode_advanced_analysis.py` with the complete endpoint set
3. Leverage parameter information for optimized API calls