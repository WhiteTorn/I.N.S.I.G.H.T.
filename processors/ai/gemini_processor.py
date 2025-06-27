"""
INSIGHT Gemini AI Processor - Single Post Analysis
=================================================

First version: Single post analyzer with JSON output
Processes unified post structure and returns markdown summary
"""

import os
import json
import logging
from typing import Dict, Any, Optional
from google import genai
from google.genai import types

class GeminiProcessor:
    """
    Gemini AI Processor for single post analysis
    
    Features:
    - Single post summarization
    - JSON output format with markdown content
    - 5-sentence limit for concise summaries
    - Robust error handling
    """
    
    def __init__(self):
        """Initialize Gemini processor"""
        self.client = None
        self.model = "gemini-2.5-flash"
        self.is_connected = False
        
    def setup_processor(self) -> bool:
        """
        Setup Gemini processor with API key validation
        
        Returns:
            bool: True if setup successful, False otherwise
        """
        try:
            api_key = os.environ.get("GEMINI_API_KEY")
            if not api_key:
                logging.error("GEMINI_API_KEY environment variable not set")
                return False
            
            self.client = genai.Client(api_key=api_key)
            logging.info("Gemini processor setup successful")
            return True
            
        except Exception as e:
            logging.error(f"Failed to setup Gemini processor: {e}")
            return False
    
    async def connect(self) -> bool:
        """
        Connect to Gemini service
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        if not self.client:
            logging.error("Processor not setup. Call setup_processor() first")
            return False
        
        try:
            # Test connection with a simple request
            test_content = [
                types.Content(
                    role="user",
                    parts=[types.Part.from_text(text="Hello")],
                ),
            ]
            
            # Quick test to validate connection
            response = self.client.models.generate_content(
                model=self.model,
                contents=test_content,
                config=types.GenerateContentConfig(
                    response_mime_type="text/plain",
                )
            )
            
            self.is_connected = True
            logging.info("Gemini processor connected successfully")
            return True
            
        except Exception as e:
            logging.error(f"Failed to connect to Gemini: {e}")
            return False
    
    async def analyze_single_post(self, post: Dict[str, Any]) -> Dict[str, str]:
        """
        Analyze a single post and return JSON summary
        
        Args:
            post: Unified post structure from any connector
            
        Returns:
            Dict with 'summary' key containing markdown-formatted summary
            Returns error message on failure
        """
        if not self.is_connected:
            return {"error": "Processor not connected. Call connect() first"}
        
        if not isinstance(post, dict):
            return {"error": "Invalid post format. Expected dictionary"}
        
        try:
            # Extract post information safely
            title = post.get('title', 'No title')
            content = post.get('content', 'No content')
            source = post.get('collection_source', 'Unknown source')
            
            # Handle different source types
            if source == 'telegram':
                channel = post.get('collection_channel', 'Unknown channel')
                source_info = f"Telegram @{channel}"
            elif source == 'rss':
                feed = post.get('collection_feed', 'Unknown feed')
                source_info = f"RSS {feed}"
            else:
                source_info = f"{source}"
            
            # Create analysis prompt
            prompt = f"""
You are an expert content analyst. Analyze this post and provide a concise, informative summary.

POST INFORMATION:
- Source: {source_info}
- Title: {title}
- Content: {content}

ANALYSIS REQUIREMENTS:
1. Provide a clear, informative summary
2. Maximum 5 sentences
3. Focus on key information and insights
4. Use markdown formatting for emphasis
5. Be objective and professional

OUTPUT FORMAT:
Return ONLY a JSON object with this exact structure:
{{"summary": "Your markdown-formatted summary here (max 5 sentences)"}}

Analyze the post now:
"""

            contents = [
                types.Content(
                    role="user",
                    parts=[types.Part.from_text(text=prompt)],
                ),
            ]
            
            generate_content_config = types.GenerateContentConfig(
                thinking_config=types.ThinkingConfig(
                    thinking_budget=-1,
                ),
                response_mime_type="text/plain",
            )

            # Get response from Gemini
            response_text = ""
            for chunk in self.client.models.generate_content_stream(
                model=self.model,
                contents=contents,
                config=generate_content_config,
            ):
                response_text += chunk.text
            
            # Parse JSON response
            try:
                # Clean response (remove any extra text)
                response_text = response_text.strip()
                if response_text.startswith('```json'):
                    response_text = response_text[7:-3].strip()
                elif response_text.startswith('```'):
                    response_text = response_text[3:-3].strip()
                
                result = json.loads(response_text)
                
                # Validate response structure
                if 'summary' not in result:
                    return {"error": "Invalid response format from AI"}
                
                return result
                
            except json.JSONDecodeError as e:
                logging.error(f"Failed to parse JSON response: {e}")
                return {"error": f"Invalid JSON response: {str(e)}"}
            
        except Exception as e:
            logging.error(f"Failed to analyze post: {e}")
            return {"error": f"Analysis failed: {str(e)}"}
    
    async def disconnect(self) -> bool:
        """
        Disconnect from Gemini service
        
        Returns:
            bool: True if disconnection successful
        """
        try:
            self.is_connected = False
            self.client = None
            logging.info("Gemini processor disconnected")
            return True
            
        except Exception as e:
            logging.error(f"Failed to disconnect Gemini processor: {e}")
            return False