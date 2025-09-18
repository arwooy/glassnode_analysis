# Glassnode Analysis System

Advanced cryptocurrency analysis system using Glassnode API data with information gain analysis, optimal prediction windows, and indicator combinations.

## Features

- **Comprehensive API Coverage**: 734 endpoints across 20 categories
- **Multi-Asset Support**: Analyze BTC, ETH, and other cryptocurrencies
- **Advanced Analytics**:
  - Information gain analysis across multiple time horizons
  - Optimal prediction window identification
  - Threshold optimization analysis
  - Indicator combination analysis (2-way and 3-way)
- **Intelligent Caching**: Disk and memory caching with parameter-aware keys
- **Robust Error Handling**: Automatic retry logic with exponential backoff
- **Rich Visualizations**: Heatmaps, threshold impact charts, combination comparisons

## Installation

```bash
git clone https://github.com/arwooy/glassnode_analysis.git
cd glassnode_analysis
pip install -r requirements.txt
```

## Quick Start

### Basic Analysis

```bash
# Analyze BTC (default)
python glassnode_advanced_analysis.py

# Analyze ETH
python glassnode_advanced_analysis.py --asset ETH

# Analyze with custom API key
python glassnode_advanced_analysis.py --asset BTC --api-key YOUR_API_KEY
```

### Test Specific Features

```bash
# Test cache functionality
python test_glassnode_cache.py

# Test asset analysis
python test_asset_analysis.py ETH

# Test endpoint loading
python test_detailed_config.py
```

## Project Structure

```
glassnode_analysis/
├── glassnode_advanced_analysis.py    # Main analysis engine
├── extract_json_from_docs.py         # Extract endpoints from documentation
├── download_glassnode_docs_v2.py     # Download API documentation
├── glassnode_endpoints_detailed.json # Complete endpoint definitions (734)
├── glassnode_cache/                  # Cached API responses
└── glassnode_docs/                   # Downloaded documentation
```

## Configuration Files

- `glassnode_endpoints_detailed.json`: Complete API endpoints with descriptions
- `glassnode_endpoints_extracted.json`: Extracted endpoint structure
- `glassnode_endpoints_final.json`: Final merged configuration

## Key Components

### 1. Data Collection
- Downloads and parses Glassnode API documentation
- Extracts 734 endpoints from OpenAPI specifications
- Supports all major endpoint categories

### 2. Analysis Engine
- **Information Gain Analysis**: Measures predictive power across time horizons
- **Optimal Window Detection**: Finds best prediction timeframes
- **Threshold Analysis**: Determines optimal indicator thresholds
- **Combination Analysis**: Tests 2-way and 3-way indicator combinations

### 3. Caching System
- Persistent disk cache in `glassnode_cache/`
- Parameter-aware cache keys
- Automatic cache loading on startup
- Reduces API calls and improves performance

### 4. Error Handling
- SSL error recovery with retry logic
- Rate limit handling
- Connection timeout management
- Up to 10 retry attempts with exponential backoff

## API Endpoints

### Categories (734 total endpoints)
- **indicators**: 158 endpoints
- **transactions**: 94 endpoints  
- **supply**: 61 endpoints
- **derivatives**: 58 endpoints
- **protocols**: 58 endpoints
- **addresses**: 50 endpoints
- **distribution**: 42 endpoints
- **breakdowns**: 39 endpoints
- **market**: 32 endpoints
- **fees**: 28 endpoints
- **eth2**: 22 endpoints
- **blockchain**: 18 endpoints
- **entities**: 18 endpoints
- **signals**: 14 endpoints
- **lightning**: 10 endpoints
- **mempool**: 10 endpoints
- **mining**: 9 endpoints
- **institutions**: 7 endpoints
- **bridges**: 5 endpoints
- **defi**: 1 endpoint

## Output Files

- `glassnode_advanced_analysis.html`: Interactive HTML report
- `glassnode_advanced_results.json`: Analysis results in JSON
- `advanced_analysis_*.png`: Visualization charts

## Requirements

```
requests>=2.28.0
pandas>=1.5.0
numpy>=1.23.0
matplotlib>=3.6.0
seaborn>=0.12.0
beautifulsoup4>=4.11.0
scipy>=1.9.0
scikit-learn>=1.2.0
```

## API Key

Get your API key from [Glassnode](https://glassnode.com)

Default test key is included but has limited access. Replace with your own key for full functionality.

## License

MIT License

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## Author

- GitHub: [@arwooy](https://github.com/arwooy)

## Acknowledgments

- Glassnode for providing comprehensive blockchain data
- OpenAPI specifications for structured endpoint documentation