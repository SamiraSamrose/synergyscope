# synergyscope - Multi-Agent AI for Esports Performance Development Platform

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
- **Live Site Demo (No API Integration)**: https://youtu.be/83SFsLXK-JA
- **Source Code**: https://youtu.be/83SFsLXK-JA
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
