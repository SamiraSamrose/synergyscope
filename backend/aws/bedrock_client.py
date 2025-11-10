# File: backend/aws/bedrock_client.py
# Purpose: AWS Bedrock client for LLM inference


"""
AWS Bedrock Client
Handles interactions with Bedrock for Claude and Titan models
"""

import boto3
import json
from typing import Dict, Any, Optional

from backend.utils.config import get_settings
from backend.utils.logger import setup_logger

settings = get_settings()
logger = setup_logger(__name__)


class BedrockClient:
    """
    Client for AWS Bedrock LLM services
    """
    
    def __init__(self):
        """Initialize Bedrock runtime client"""
        self.bedrock_runtime = boto3.client(
            'bedrock-runtime',
            region_name=settings.AWS_REGION
        )
        self.model_id = settings.BEDROCK_MODEL_ID
        logger.info(f"Bedrock client initialized with model: {self.model_id}")
    
    async def generate_text(
        self,
        prompt: str,
        max_tokens: int = 500,
        temperature: float = 0.7,
        top_p: float = 0.9
    ) -> str:
        """
        Generate text using Bedrock Claude model
        
        Args:
            prompt: Input prompt
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            top_p: Nucleus sampling parameter
            
        Returns:
            Generated text
        """
        try:
            # Prepare request for Claude
            request_body = {
                "prompt": f"\n\nHuman: {prompt}\n\nAssistant:",
                "max_tokens_to_sample": max_tokens,
                "temperature": temperature,
                "top_p": top_p,
                "stop_sequences": ["\n\nHuman:"]
            }
            
            response = self.bedrock_runtime.invoke_model(
                modelId=self.model_id,
                body=json.dumps(request_body)
            )
            
            response_body = json.loads(response['body'].read())
            generated_text = response_body.get('completion', '').strip()
            
            logger.info("Text generation completed")
            return generated_text
            
        except Exception as e:
            logger.error(f"Text generation failed: {e}")
            return "Unable to generate text at this time."
    
    async def generate_structured_output(
        self,
        prompt: str,
        output_schema: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate structured JSON output
        
        Args:
            prompt: Input prompt with schema instructions
            output_schema: Expected output schema
            
        Returns:
            Parsed JSON output
        """
        try:
            enhanced_prompt = f"""
            {prompt}
            
            Respond ONLY with valid JSON matching this schema:
            {json.dumps(output_schema, indent=2)}
            
            Do not include any explanatory text, only the JSON object.
            """
            
            generated = await self.generate_text(enhanced_prompt, max_tokens=1000)
            
            # Clean and parse JSON
            json_str = generated.strip()
            if json_str.startswith('```json'):
                json_str = json_str.split('```json')[1].split('```')[0]
            elif json_str.startswith('```'):
                json_str = json_str.split('```')[1].split('```')[0]
            
            parsed = json.loads(json_str)
            return parsed
            
        except Exception as e:
            logger.error(f"Structured output generation failed: {e}")
            return {}