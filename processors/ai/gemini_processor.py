"""
INSIGHT Gemini AI Processor - Single Post Analysis
=================================================

First version: Single post analyzer with JSON output
Processes unified post structure and returns markdown summary
"""

import os
import json
import logging
from typing import Dict, Any, Optional, List
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
1. Provide a clear, briefing summary | user should spend as less time as possible understading the main idea of the post.
2. Maximum 5 sentences | maximum does not mean that you should use all 5 sentences.
3. Focus on key information and insights
4. Use markdown formatting for emphasis (bold, italic, links, etc.)
5. Be objective and professional

OUTPUT FORMAT:
Return ONLY the markdown-formatted summary text. Do not include any JSON formatting or code blocks.

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
            
            # Clean and wrap response manually
            summary = response_text.strip()
            
            # Remove any code block formatting if present
            if summary.startswith('```'):
                summary = summary.split('\n', 1)[1] if '\n' in summary else summary[3:]
            if summary.endswith('```'):
                summary = summary.rsplit('\n', 1)[0] if '\n' in summary else summary[:-3]
            
            # Manually create JSON structure
            return {"summary": summary.strip()}
            
        except Exception as e:
            logging.error(f"Failed to analyze post: {e}")
            return {"error": f"Analysis failed: {str(e)}"}
    
    async def ask_single_post(self, post: Dict[str, Any], question: str) -> Dict[str, str]:
        """
        Ask Gemini to analyze a single post and return the response
        
        Args:
            post: Unified post structure from any connector

        output:
            Json of the answer from Gemini.
        """

        if not self.is_connected:
            return {"error": "Processor not connected. Call connect() first"}
        
        if not isinstance(post, dict):
            return {"error": "Invalid post format. Expected dictionary"}
        
        if not isinstance(question, str):
            return {"error": "Invalid question format. Expected string"}
        
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
You are an expert content analyst. Analyze this content and answer the question that user will provide to you.

POST INFORMATION:
- Source: {source_info}
- Title: {title}
- Content: {content}

ANALYSIS REQUIREMENTS:
1. Provide a clear, briefing answer | user should spend as less time as possible understading the main idea of the content.
2. Maximum 5 sentences | maximum does not mean that you should use all 5 sentences.
3. Focus on key information and insights
4. Use markdown formatting for emphasis (bold, italic, links, etc.)
5. Be objective and professional

OUTPUT FORMAT:
Return ONLY the markdown-formatted answer text. Do not include any JSON formatting or code blocks.

Answer the question now:
- Question: {question}
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
            
            # Clean and wrap response manually
            answer = response_text.strip()
            
            # Remove any code block formatting if present
            if answer.startswith('```'):
                answer = answer.split('\n', 1)[1] if '\n' in answer else answer[3:]
            if answer.endswith('```'):
                answer = answer.rsplit('\n', 1)[0] if '\n' in answer else answer[:-3]
            
            # Manually create JSON structure
            return {"answer": answer.strip()}
            
        except Exception as e:
            logging.error(f"Failed to analyze post: {e}")
            return {"error": f"Analysis failed: {str(e)}"}
    

    async def daily_briefing(self, posts: List[Dict[str, Any]]) -> Dict[str, str]:
        """
        Generate a daily briefing for a list of posts

        Args:
            posts: List of unified post structures
            
        """

        if not self.is_connected:
            return {"error": "Processor not connected. Call connect() first"}
        
        if not isinstance(posts, list):
            return {"error": "Invalid posts format. Expected list"}
        
        try:
            prompt = f"""
            You are an export content analyzer, working on the president's desk. 30 year in providing daily briefings to the president.
            You will receice series of different content from the different sources. your task would be to provide
            - concise summary of the content that president will understand and act upon.
            - your briefing should generate insights, should be clear, engaging and interesting to the president.
            - remember that president is busy person, so your briefing should be very concise and to the point.
            - but concise does not mean that you should not provide any insights, you should provide as much insights as possible without losing actual point.
            because if you lose the point, the whole country will be in danger.

            - Briefing should be 15 minutes long maximum. most important topics at the beginning.

            QUALITY CONTROLS:
            - Flag any unverified information clearly
            - Note conflicting sources or uncertain intelligence
            - Escalate items requiring immediate attention
            - Cross-reference with established US policy positions

            The President needs clarity to make informed decisions that affect millions of lives. 
            Balance brevity with completeness - every word should serve a purpose.

            Here is the content:
            {posts}

            do not mention that you are talking to the president, just provide the briefing.

            example of the briefing:

            Today we have 3 main topics to discuss:
            1. Topic 1
            - Key point 1
            - Key point 2
            2. Topic 2
            3. Topic 3

            Output Format is Strictly Followed Markdown Format:

            Actual Briefing:
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

            # Clean and wrap response manually
            briefing = response_text.strip()
            
            # Remove any code block formatting if present
            if briefing.startswith('```'):
                briefing = briefing.split('\n', 1)[1] if '\n' in briefing else briefing[3:]
            if briefing.endswith('```'):
                briefing = briefing.rsplit('\n', 1)[0] if '\n' in briefing else briefing[:-3]
            
            # Manually create JSON structure
            return {"briefing": briefing.strip()}
            
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