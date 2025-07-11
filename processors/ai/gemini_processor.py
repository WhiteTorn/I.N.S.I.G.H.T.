"""
INSIGHT Gemini AI Processor - Single Post Analysis with Token Tracking
====================================================================

Enhanced version with token counting capabilities
Processes unified post structure and returns markdown summary with token usage
"""

import os
import json
import logging
import time
from typing import Dict, Any, Optional, List, Tuple
from google import genai
from google.genai import types

class GeminiProcessor:
    """
    Gemini AI Processor for single post analysis with token tracking
    
    Features:
    - Single post summarization
    - JSON output format with markdown content
    - 5-sentence limit for concise summaries
    - Token usage tracking for input and output
    - Robust error handling
    """
    
    def __init__(self):
        """Initialize Gemini processor"""
        self.client = None
        self.model = "gemini-2.0-flash"  # Updated to 2.0-flash for token counting
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
            test_prompt = "Hello"
            
            # Quick test to validate connection
            response = self.client.models.generate_content(
                model=self.model,
                contents=test_prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="text/plain",
                    temperature=0.1
                )
            )
            
            self.is_connected = True
            logging.info("Gemini processor connected successfully")
            return True
            
        except Exception as e:
            logging.error(f"Failed to connect to Gemini: {e}")
            return False

    def count_tokens(self, content: str) -> int:
        """Count tokens in content using Gemini's token counting API"""
        if not self.is_connected:
            logging.error("Processor not connected. Call connect() first")
            return 0
        
        try:
            total_tokens = self.client.models.count_tokens(
                model=self.model, 
                contents=content
            )
            # Removed: time.sleep(10)  # This was causing performance issues
            return total_tokens
        except Exception as e:
            logging.error(f"Failed to count tokens: {e}")
            return 0

    async def analyze_single_post_with_tokens(self, post: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze a single post and return JSON summary with token usage
        
        Args:
            post: Unified post structure from any connector
            
        Returns:
            Dict with 'summary' key and token usage information
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

            # Count input tokens
            input_tokens = self.count_tokens(prompt)

            # Generate content with non-streaming for token metadata
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="text/plain",
                    temperature=0.1
                )
            )
            
            # Get token usage metadata
            usage_metadata = response.usage_metadata if hasattr(response, 'usage_metadata') else None
            
            # Clean response text
            summary = response.text.strip()
            
            # Remove any code block formatting if present
            if summary.startswith('```'):
                summary = summary.split('\n', 1)[1] if '\n' in summary else summary[3:]
            if summary.endswith('```'):
                summary = summary.rsplit('\n', 1)[0] if '\n' in summary else summary[:-3]
            
            # Prepare token information
            token_info = {
                "input_tokens_counted": input_tokens,
                "prompt_tokens": usage_metadata.prompt_token_count if usage_metadata else None,
                "response_tokens": usage_metadata.candidates_token_count if usage_metadata else None,
                "total_tokens": usage_metadata.total_token_count if usage_metadata else None
            }
            
            # Return with token information
            return {
                "summary": summary.strip(),
                "token_usage": token_info
            }
            
        except Exception as e:
            logging.error(f"Failed to analyze post: {e}")
            return {"error": f"Analysis failed: {str(e)}"}

    async def ask_single_post_with_tokens(self, post: Dict[str, Any], question: str) -> Dict[str, Any]:
        """
        Ask Gemini to analyze a single post and return the response with token usage
        
        Args:
            post: Unified post structure from any connector
            question: Question to ask about the post

        Returns:
            Dict with answer and token usage information
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

            # Count input tokens
            input_tokens = self.count_tokens(prompt)

            # Generate content with non-streaming for token metadata
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="text/plain",
                    temperature=0.1
                )
            )
            
            # Get token usage metadata
            usage_metadata = response.usage_metadata if hasattr(response, 'usage_metadata') else None
            
            # Clean response text
            answer = response.text.strip()
            
            # Remove any code block formatting if present
            if answer.startswith('```'):
                answer = answer.split('\n', 1)[1] if '\n' in answer else answer[3:]
            if answer.endswith('```'):
                answer = answer.rsplit('\n', 1)[0] if '\n' in answer else answer[:-3]
            
            # Prepare token information
            token_info = {
                "input_tokens_counted": input_tokens,
                "prompt_tokens": usage_metadata.prompt_token_count if usage_metadata else None,
                "response_tokens": usage_metadata.candidates_token_count if usage_metadata else None,
                "total_tokens": usage_metadata.total_token_count if usage_metadata else None
            }
            
            # Return with token information
            return {
                "answer": answer.strip(),
                "token_usage": token_info
            }
            
        except Exception as e:
            logging.error(f"Failed to analyze post: {e}")
            return {"error": f"Analysis failed: {str(e)}"}

    async def daily_briefing_with_tokens(self, posts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate a daily briefing for a list of posts with token tracking

        Args:
            posts: List of unified post structures
            
        Returns:
            Dict with briefing content and token usage information
        """
        if not self.is_connected:
            return {"error": "Processor not connected. Call connect() first"}
        
        if not isinstance(posts, list):
            return {"error": "Invalid posts format. Expected list"}
        
        try:
            prompt = f"""
            You are an expert content analyzer, working with Tony Stark. You call user as Master.
            Your name is Insight. 30 year in providing daily briefings to the Mr. Stark.
            
            You will receice series of different content from the different sources. your task would be to provide
            - concise summary of the content that Mr. Stark will understand and act upon.
            - your briefing should generate insights, should be clear, engaging and interesting to the Mr. Stark, Which should stimulate the Mr. Stark to take action.
            - remember that Mr. Stark is busy person, so your briefing should be very concise and to the point.
            - but concise does not mean that you should not provide any insights, you should provide as much insights as possible without losing actual point.
            - Include relevant historical context or analogies when helpful
            - Adapt language and tone to match the Mr. Stark's background and interests
            because if you lose the point, the whole world will be in danger.

            - Briefing should be 15 minutes long. most important topics at the beginning.

            QUALITY CONTROLS:
            - Flag any unverified information clearly
            - Note conflicting sources or uncertain intelligence
            - Escalate items requiring immediate attention

            - Topics must be specific and descriptive (e.g., "Meta's New AI Model Launch" instead of "Topic 1")
            - Each topic should include:
                * Specific event/development
                * Direct impact on Global interests
                * Recommended actions or considerations

            - Use bullet points for quick scanning
            - Bold key terms and critical information

            The Mr.Stark needs clarity to make informed decisions that affect millions of lives. 
            Balance brevity with completeness - every word should serve a purpose.
            Remember your briefing should not be replacement of the news, it should be a supplement to the news, you should give new insights, new ideas, new perspectives!!!

            Here is the content:
            {posts}

            do not mention that you are talking to the Mr.Stark, just provide the briefing.

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

            # Count input tokens
            input_tokens = self.count_tokens(prompt)

            # Generate content with non-streaming for token metadata
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="text/plain",
                    temperature=0.1
                )
            )
            
            # Get token usage metadata
            usage_metadata = response.usage_metadata if hasattr(response, 'usage_metadata') else None
            
            # Clean response text
            briefing = response.text.strip()
            
            # Remove any code block formatting if present
            if briefing.startswith('```'):
                briefing = briefing.split('\n', 1)[1] if '\n' in briefing else briefing[3:]
            if briefing.endswith('```'):
                briefing = briefing.rsplit('\n', 1)[0] if '\n' in briefing else briefing[:-3]
            
            # Prepare token information
            token_info = {
                "input_tokens_counted": input_tokens,
                "prompt_tokens": usage_metadata.prompt_token_count if usage_metadata else None,
                "response_tokens": usage_metadata.candidates_token_count if usage_metadata else None,
                "total_tokens": usage_metadata.total_token_count if usage_metadata else None
            }
            
            return {
                "briefing": briefing.strip(),
                "token_usage": token_info
            }
            
        except Exception as e:
            logging.error(f"Failed to analyze post: {e}")
            return {"error": f"Analysis failed: {str(e)}"}

    # Keep the original methods for backward compatibility
    async def analyze_single_post(self, post: Dict[str, Any]) -> Dict[str, str]:
        """
        Original analyze_single_post method for backward compatibility
        """
        result = await self.analyze_single_post_with_tokens(post)
        if "error" in result:
            return result
        return {"summary": result["summary"]}

    async def ask_single_post(self, post: Dict[str, Any], question: str) -> Dict[str, str]:
        """
        Original ask_single_post method for backward compatibility
        """
        result = await self.ask_single_post_with_tokens(post, question)
        if "error" in result:
            return result
        return {"answer": result["answer"]}

    async def daily_briefing(self, posts: List[Dict[str, Any]]) -> str:
        """
        Original daily_briefing method for backward compatibility
        """
        result = await self.daily_briefing_with_tokens(posts)
        if "error" in result:
            return result["error"]
        return result["briefing"]

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
        
    async def enhanced_daily_briefing_with_topics(self, posts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Enhanced daily briefing generation that includes topic extraction and post references
        """
        if not self.is_connected:
            return {"error": "Processor not connected. Call connect() first"}
        
        if not isinstance(posts, list):
            return {"error": "Invalid posts format. Expected list"}
        
        try:
            # Format posts with URLs/IDs for reference
            formatted_posts = []
            for i, post in enumerate(posts):
                post_id = post.get('url', f"post_{i}")
                post_content = {
                    "id": post_id,
                    "title": post.get('title', ''),
                    "content": post.get('content', ''),
                    "source": post.get('source', ''),
                    "date": str(post.get('date', ''))
                }
                formatted_posts.append(post_content)
            
            # Simplified prompt that requests text format but structured
            prompt = f"""
You are an expert intelligence analyst working with Tony Stark.
Your name is Insight. 30 years providing daily briefings.

MISSION: Analyze {len(posts)} posts and create enhanced daily briefing.

STEP 1: Generate standard daily briefing
STEP 2: Extract 3-5 main topics from the posts
STEP 3: Create topic summaries with post references

OUTPUT FORMAT - Use this EXACT structure:

===DAILY_BRIEFING_START===
[Your normal briefing here - same format as always]
===DAILY_BRIEFING_END===

===TOPICS_START===
Topic 1: [Topic Title]
ID: topic-1
Summary: [Detailed analysis of this topic]
Posts: post_0, post_2, post_4

Topic 2: [Topic Title]  
ID: topic-2
Summary: [Detailed analysis of this topic]
Posts: post_1, post_3

Topic 3: [Topic Title]
ID: topic-3  
Summary: [Detailed analysis of this topic]
Posts: post_5, post_6
===TOPICS_END===

POSTS DATA:
{formatted_posts}

Generate the response now:
"""

            # Use text format instead of JSON
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="text/plain",  # Changed from application/json
                    temperature=0.1
                )
            )
            
            # Get token usage metadata  
            usage_metadata = response.usage_metadata if hasattr(response, 'usage_metadata') else None
            
            # Parse the structured text response
            response_text = response.text.strip()
            
            # Extract daily briefing
            daily_briefing = ""
            if "===DAILY_BRIEFING_START===" in response_text and "===DAILY_BRIEFING_END===" in response_text:
                start = response_text.find("===DAILY_BRIEFING_START===") + len("===DAILY_BRIEFING_START===")
                end = response_text.find("===DAILY_BRIEFING_END===")
                daily_briefing = response_text[start:end].strip()
            
            # Extract topics
            topics = []
            table_of_contents = []
            
            if "===TOPICS_START===" in response_text and "===TOPICS_END===" in response_text:
                start = response_text.find("===TOPICS_START===") + len("===TOPICS_START===")
                end = response_text.find("===TOPICS_END===")
                topics_text = response_text[start:end].strip()
                
                # Parse topics (simple text parsing)
                current_topic = {}
                for line in topics_text.split('\n'):
                    line = line.strip()
                    if line.startswith('Topic ') and ':' in line:
                        # Save previous topic
                        if current_topic:
                            topics.append(current_topic)
                            table_of_contents.append({
                                "id": current_topic["id"],
                                "title": current_topic["title"]
                            })
                        # Start new topic
                        title = line.split(':', 1)[1].strip()
                        current_topic = {"title": title, "summary": "", "post_references": []}
                    elif line.startswith('ID:'):
                        current_topic["id"] = line.split(':', 1)[1].strip()
                    elif line.startswith('Summary:'):
                        current_topic["summary"] = line.split(':', 1)[1].strip()
                    elif line.startswith('Posts:'):
                        posts_str = line.split(':', 1)[1].strip()
                        current_topic["post_references"] = [p.strip() for p in posts_str.split(',')]
                    elif line and current_topic.get("summary"):
                        # Continue summary on next lines
                        current_topic["summary"] += " " + line
                
                # Add last topic
                if current_topic:
                    topics.append(current_topic)
                    table_of_contents.append({
                        "id": current_topic["id"], 
                        "title": current_topic["title"]
                    })
            
            # Prepare token information
            token_info = {
                "input_tokens_counted": 0,  # Skip token counting for now to avoid sleep
                "prompt_tokens": usage_metadata.prompt_token_count if usage_metadata else None,
                "response_tokens": usage_metadata.candidates_token_count if usage_metadata else None,
                "total_tokens": usage_metadata.total_token_count if usage_metadata else None
            }
            
            # Build result
            result = {
                "daily_briefing": daily_briefing,
                "table_of_contents": table_of_contents,
                "topics": topics,
                "token_usage": token_info
            }
            
            return result
            
        except Exception as e:
            logging.error(f"Failed to generate enhanced briefing: {e}")
            return {"error": f"Enhanced briefing generation failed: {str(e)}"}