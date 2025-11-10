# SynergyScope - Multi-Agent AI for Esports Performance Development Platform

SynergyScope is an advanced AI-powered analytics platform that maps social synergy, tracks meta adaptation, and predicts optimal team compositions in League of Legends using multi-agent architecture on AWS.

## Features

- **Social Graph Analysis**: Dynamic relationship mapping between players
- **Chemistry Quantification**: GNN-based synergy detection and friction zone identification
- **Meta Tracking**: Patch-based performance analysis and meta shift correlation
- **Adaptation Modeling**: Time-series forecasting of player and team learning curves
- **Predictive Recommendations**: AI-driven team composition suggestions
- **Generative Narratives**: Natural language summaries of team evolution
- **Interactive Visualizations**: Comprehensive dashboards with synergy graphs, heatmaps, and timelines

## Links
- **Live Site Demo (No API Integration)**: https://samirasamrose.github.io/synergyscope/
- **Source Code**: https://github.com/SamiraSamrose/synergyscope
- **Video Demo**: https://youtu.be/83SFsLXK-JA


## Architecture

SynergyScope employs a multi-agent system architecture with seven specialized agents:

1. **Social Graph Agent**: Builds player relationship graphs using AWS Neptune
2. **Chemistry Analyst Agent**: Quantifies synergy using SageMaker GNN models
3. **Meta Analyst Agent**: Tracks patch changes using Glue and Athena
4. **Adaptation Agent**: Models learning curves using SageMaker Forecast
5. **Compatibility Agent**: Recommends compositions using SageMaker and Bedrock
6. **Storyteller Agent**: Generates insights using Bedrock Claude/Titan
7. **Visualizer Agent**: Creates dashboards using QuickSight and Amplify

## Technology Stack

- **Backend**: Python 3.11+, FastAPI
- **Frontend**: HTML5, CSS3, JavaScript (D3.js, Chart.js, Three.js)
- **AWS Services**: Lambda, Glue, Neptune, SageMaker, Bedrock, QuickSight, S3, API Gateway
- **ML Models**: Graph Neural Networks, DeepAR, Time Series Forecasting
- **Infrastructure**: Terraform, Docker

## Prerequisites

- Python 3.11 or higher
- AWS Account with appropriate permissions
- Riot Games API key
- Node.js 18+ (for frontend build tools)
- Terraform 1.5+ (for infrastructure deployment)
- Docker and Docker Compose (for local development)

##AWS AI Services Implementation

- Amazon Bedrock (Claude/Titan Models): 
Bedrock serves as the narrative intelligence layer, transforming structured analytical outputs into natural language insights. The service receives JSON-formatted data containing synergy scores, adaptation metrics, and performance trends from upstream agents. Claude models generate contextual summaries like "Team synergy peaked in patch 14.13 driven by control-style compositions," translating statistical patterns into actionable coaching advice. Bedrock's API integration through Lambda enables real-time insight generation without managing model infrastructure.

- Amazon SageMaker (Machine Learning Training & Inference): 
SageMaker hosts three distinct model types for specialized analysis. Graph Neural Network models built with PyTorch Geometric process Neptune relationship data to detect synergy patterns that traditional metrics miss, learning which player pairs exhibit coordinated behavior beyond simple win rates. DeepAR time-series models forecast adaptation curves by analyzing performance trajectories across patch transitions. SageMaker Recommender algorithms combine historical synergy data with predicted meta shifts to suggest optimal team compositions, outputting ranked recommendations with confidence scores.

- Amazon Neptune (Graph Database): 
Neptune stores the social graph where nodes represent players and edges encode relationship metrics like co-play frequency, win rates, and role combinations. The graph structure enables efficient traversal queries for finding high-synergy pairs and detecting communities within larger player networks. GNN models train directly on this graph topology, leveraging Neptune's Gremlin API for batch data extraction during model training cycles.

- AWS Glue (ETL & Data Preparation): 
Glue ETL jobs transform raw JSON match data from Riot API into structured formats suitable for analysis. Jobs parse nested timeline events to extract coordinated play indicators, aggregate player statistics across match sequences, and join performance data with patch metadata based on timestamps. Glue Data Catalog creates schemas that enable Athena to query processed datasets stored in S3 partitioned by date and player.

- Amazon Athena (Query Engine): 
Athena executes SQL queries against S3 data lakes to compute aggregations needed for agent analysis. Queries calculate patch-specific win rates, champion mastery distributions, and performance deltas before/after balance changes. The Meta Tracker agent relies on Athena to correlate performance shifts with specific patch notes by temporal analysis of match outcomes.

- AWS Lambda (Serverless Compute): 
Lambda functions orchestrate the entire data pipeline from API ingestion through insight delivery. Functions trigger on EventBridge schedules to fetch new match data, invoke SageMaker endpoints for real-time predictions, call Bedrock APIs for narrative generation, and aggregate results into DynamoDB. The serverless model eliminates infrastructure management while scaling automatically during batch processing jobs.

- Amazon QuickSight (Analytics Visualization): 
QuickSight dashboards connect directly to Neptune, Athena, and DynamoDB to visualize synergy networks, adaptation heatmaps, and performance trends. SPICE in-memory engine caches frequently accessed datasets for sub-second query response. Embedded dashboards in the Amplify frontend provide interactive filtering without requiring separate BI tool access.

- AWS Step Functions (Workflow Orchestration): 
Step Functions coordinate multi-agent workflows where outputs from one agent serve as inputs to downstream analysis. A typical workflow sequences Graph Builder extracting Neptune data, Chemistry Analyst running GNN inference, Meta Tracker querying patch correlations, Adaptation Agent calculating learning curves, Forecaster generating predictions, and Storyteller producing narratives. Error handling and retry logic ensure pipeline reliability.

##Data Sources and Processing

- Riot Games API Endpoints: 
The platform consumes data from summoner-v4 (player profiles), match-v5 (detailed match history with timeline events), league-v4 (ranked tier information), and champion-mastery-v4 (champion proficiency scores). API Gateway proxies requests through Lambda with rate limiting and caching in DynamoDB to respect Riot's API quotas while maintaining data freshness.

- Match Timeline Data: 
Timeline events within match-v5 responses capture frame-by-frame game state including player positions, ability usage, and objective timings. This granular data feeds synergy detection algorithms that identify coordinated plays like synchronized engages or vision control patterns that raw statistics miss.

- Patch Metadata: 
External data sources providing patch notes, item changes, and champion balance adjustments are scraped and stored in S3. Glue jobs parse this unstructured text to create structured patch impact records that the Meta Tracker correlates with performance changes.

- Graph Relationship Encoding: 
Neptune edges store weighted relationships calculated from match data: co-play frequency (number of matches together), win rate when paired, average gold differential, and role-specific synergy scores. Node properties include player rank, champion pools, and historical performance metrics that GNN models use as feature vectors.

- Training Dataset Construction: 
SageMaker training jobs pull historical match data spanning multiple patches to build datasets where each sample represents a player-pair with features including aggregate statistics, champion overlap, and temporal context. Labels for supervised learning include actual win outcomes and measured synergy indicators derived from coordinated play detection algorithms.

- Real-Time Data Flow: 
Live analysis mode fetches recent matches via Lambda triggered by EventBridge rules, processes through Glue streaming ETL, updates Neptune graph incrementally, invokes SageMaker endpoints for inference, and pushes results to frontend through AppSync WebSocket connections enabling near real-time dashboard updates.

## Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/synergyscope.git
cd synergyscope
```

### 2. Environment Setup

```bash
cp .env.example .env
# Edit .env with your AWS credentials and API keys
```

### 3. Install Dependencies

```bash
# Backend dependencies
cd backend
pip install -r requirements.txt

# Or use virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 4. AWS Infrastructure Setup

```bash
# Navigate to infrastructure directory
cd ../infrastructure/terraform

# Initialize Terraform
terraform init

# Review planned changes
terraform plan

# Deploy infrastructure
terraform apply
```

### 5. Run Local Development Server

```bash
# From project root
python scripts/run_demo.py

# Or manually
cd backend
uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
```

Access the application at `http://localhost:8000`

## Configuration

Edit `.env` file with your credentials:

```env
# AWS Configuration
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key

# Riot API
RIOT_API_KEY=your_riot_api_key
RIOT_API_REGION=na1

# Neptune
NEPTUNE_ENDPOINT=your_neptune_endpoint
NEPTUNE_PORT=8182

# SageMaker
SAGEMAKER_ENDPOINT=your_sagemaker_endpoint

# Bedrock
BEDROCK_MODEL_ID=anthropic.claude-v2

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_WORKERS=4
```

## Detailed Setup Guide

See [docs/AWS_SETUP.md](docs/AWS_SETUP.md) for comprehensive AWS configuration instructions.

## Usage

### Demo Mode

```bash
python scripts/run_demo.py --mode demo
```

The demo provides:
- Interactive UI for testing all agents
- Sample data visualization
- Agent-by-agent walkthrough
- Real-time synergy calculations
- Patch adaptation tracking

### Production Mode

```bash
# Start backend API
uvicorn api.main:app --host 0.0.0.0 --port 8000

# Process match history
python scripts/seed_data.py --summoner-name "YourSummonerName" --region "na1"
```

## API Endpoints

### Core Endpoints

- `GET /api/v1/health` - Health check
- `POST /api/v1/summoner/analyze` - Analyze summoner match history
- `GET /api/v1/synergy/graph/{summoner_id}` - Get synergy graph
- `GET /api/v1/meta/evolution/{summoner_id}` - Get meta adaptation data
- `GET /api/v1/predictions/compositions` - Get team composition recommendations
- `GET /api/v1/insights/narrative/{summoner_id}` - Get AI-generated narrative

See [docs/API_REFERENCE.md](docs/API_REFERENCE.md) for complete API documentation.

## Testing

```bash
# Run all tests
pytest tests/

# Run specific test suite
pytest tests/test_agents.py

# Run with coverage
pytest --cov=backend tests/
```

## Deployment

### Docker Deployment

```bash
docker-compose up -d
```

### AWS Deployment

```bash
./scripts/deploy.sh production
```

See [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) for detailed deployment instructions.

## Project Highlights

- **Multi-Agent Collaboration**: Agents communicate through event-driven architecture
- **Graph Neural Networks + Time-Series Fusion**: Combines relationship analysis with temporal modeling
- **Generative Narrative Engine**: Converts statistics into engaging storytelling
- **Meta-Adaptive Recommendations**: Predicts performance under future meta scenarios
- **Scalable AWS Architecture**: Serverless, cost-efficient, extensible design


## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for contribution guidelines.

## License

MIT License - see [LICENSE](LICENSE) file for details.
