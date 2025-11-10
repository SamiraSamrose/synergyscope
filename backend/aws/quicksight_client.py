# File: backend/aws/quicksight_client.py
# Purpose: AWS QuickSight dashboard management

"""
AWS QuickSight Client
Manages dashboard creation and visualization
"""

import boto3
from typing import Dict, List, Any

from backend.utils.config import get_settings
from backend.utils.logger import setup_logger

settings = get_settings()
logger = setup_logger(__name__)


class QuickSightClient:
    """
    Client for AWS QuickSight dashboard operations
    """
    
    def __init__(self):
        """Initialize QuickSight client"""
        self.quicksight = boto3.client('quicksight', region_name=settings.AWS_REGION)
        self.account_id = settings.QUICKSIGHT_ACCOUNT_ID
        logger.info("QuickSight client initialized")
    
    async def create_synergy_dashboard(
        self,
        dashboard_name: str,
        data_source_arn: str
    ) -> str:
        """
        Create synergy analysis dashboard
        
        Args:
            dashboard_name: Name for the dashboard
            data_source_arn: ARN of data source
            
        Returns:
            Dashboard ID
        """
        try:
            # Define dashboard structure
            dashboard_definition = {
                'DataSetIdentifierDeclarations': [{
                    'Identifier': 'synergy_data',
                    'DataSetArn': data_source_arn
                }],
                'Sheets': [{
                    'SheetId': 'synergy_sheet',
                    'Name': 'Synergy Analysis',
                    'Visuals': [
                        self._create_network_visual(),
                        self._create_heatmap_visual(),
                        self._create_timeline_visual()
                    ]
                }]
            }
            
            response = self.quicksight.create_dashboard(
                AwsAccountId=self.account_id,
                DashboardId=f'synergyscope-{dashboard_name}',
                Name=dashboard_name,
                Definition=dashboard_definition
            )
            
            dashboard_id = response['DashboardId']
            logger.info(f"Dashboard created: {dashboard_id}")
            return dashboard_id
            
        except Exception as e:
            logger.error(f"Dashboard creation failed: {e}")
            raise
    
    def _create_network_visual(self) -> Dict[str, Any]:
        """Create network graph visual configuration"""
        return {
            'VisualId': 'network_visual',
            'GraphVisual': {
                'Title': {'Visibility': 'VISIBLE', 'FormatText': {'PlainText': 'Player Synergy Network'}},
                'ChartConfiguration': {
                    'FieldWells': {
                        'Nodes': [{'CategoricalDimensionField': {'FieldId': 'player_id'}}],
                        'Edges': [{'NumericalMeasureField': {'FieldId': 'synergy_score'}}]
                    }
                }
            }
        }
    
    def _create_heatmap_visual(self) -> Dict[str, Any]:
        """Create heatmap visual configuration"""
        return {
            'VisualId': 'heatmap_visual',
            'HeatMapVisual': {
                'Title': {'Visibility': 'VISIBLE', 'FormatText': {'PlainText': 'Adaptation Heatmap'}},
                'ChartConfiguration': {
                    'FieldWells': {
                        'Rows': [{'CategoricalDimensionField': {'FieldId': 'patch'}}],
                        'Values': [{'NumericalMeasureField': {'FieldId': 'win_rate'}}]
                    },
                    'ColorScale': {
                        'Colors': [
                            {'Color': '#ff4444'},
                            {'Color': '#ffaa00'},
                            {'Color': '#00c896'}
                        ]
                    }
                }
            }
        }
    
    def _create_timeline_visual(self) -> Dict[str, Any]:
        """Create timeline visual configuration"""
        return {
            'VisualId': 'timeline_visual',
            'LineChartVisual': {
                'Title': {'Visibility': 'VISIBLE', 'FormatText': {'PlainText': 'Meta Evolution Timeline'}},
                'ChartConfiguration': {
                    'FieldWells': {
                        'XAxis': [{'DateDimensionField': {'FieldId': 'patch_date'}}],
                        'Values': [{'NumericalMeasureField': {'FieldId': 'performance'}}]
                    }
                }
            }
        }
