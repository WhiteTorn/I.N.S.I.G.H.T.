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
You are Insight — Tony Stark's senior intelligence companion. Deliver a complete, self-sufficient briefing so Stark can act without opening the sources.

Directive
- Be decisive, analytical, and surgical. Avoid filler. Use crisp markdown.
- Synthesize across sources; infer second- and third-order effects.
- Call out risks, opportunities, and time-sensitive moves. If facts conflict, say so.

Output (markdown only)
## Global Situation Briefing
- 10–15 bullets that explain what happened and why it matters. Connect dots across tech, markets, security, and geopolitics. Prefer specifics over generalities.

## Strategic Implications
- Markets: 3–5 bullets (capital flows, regulatory posture, enterprise adoption).
- Technology: 3–5 bullets (capabilities, constraints, moats, infra shifts).
- Security/Privacy: 2–4 bullets (attack surface, failures, mitigations).
- Geopolitics: 2–4 bullets (state actors, alliances, export controls).

## Early Warning Signals (Leading Indicators)
- 5–8 bullets. Name concrete metrics, datasets, or events to watch next.

## Recommended Actions (Next 24–72h)
- 5–10 bullets. Clear, testable actions with intended outcome. Use strong verbs.

Constraints
- No code blocks. No JSON. No acknowledgements. Just the briefing.

Intelligence Package
{posts}
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
            # Format posts with actual URLs for reference
            formatted_posts = []
            post_references = []  # Keep track of actual post IDs
            
            for i, post in enumerate(posts):
                post_url = post.get('url', f"post_{i}")
                post_references.append(post_url)
                
                post_content = {
                    "url": post_url,
                    "title": post.get('title', ''),
                    "content": post.get('content', ''),
                    "source": post.get('source', ''),
                    "date": str(post.get('date', ''))
                }
                formatted_posts.append(post_content)
            
            # Create example reference format for the prompt
            example_refs = ", ".join(post_references[:3]) if len(post_references) >= 3 else ", ".join(post_references)
            
            # Updated prompt that uses actual URLs for references
            prompt = f"""
You are an expert intelligence analyst working with Tony Stark.
Your name is Insight. 30 years providing daily briefings.

MISSION: Analyze {len(posts)} posts and create enhanced daily briefing.

STEP 1: Generate standard daily briefing
STEP 2: Extract 3-5 main topics from the posts
STEP 3: Create topic summaries with post references

IMPORTANT: When referencing posts, use their ACTUAL URLs, not generic post_0, post_1, etc.

OUTPUT FORMAT - Use this EXACT structure:

===DAILY_BRIEFING_START===
[Your normal briefing here - same format as always]
===DAILY_BRIEFING_END===

===TOPICS_START===
Topic 1: [Topic Title]
ID: topic-1
Summary: [Detailed analysis of this topic]
Posts: {example_refs}

Topic 2: [Topic Title]  
ID: topic-2
Summary: [Detailed analysis of this topic]
Posts: [actual URLs from the posts, comma separated]

Topic 3: [Topic Title]
ID: topic-3  
Summary: [Detailed analysis of this topic]
Posts: [actual URLs from the posts, comma separated]
===TOPICS_END===

Available post URLs for reference:
{chr(10).join(post_references)}

POSTS DATA:
{formatted_posts}

Generate the response now using ACTUAL URLs in the Posts: lines:
"""

            # Use text format instead of JSON
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
                        # Clean up the URLs and split properly
                        current_topic["post_references"] = [p.strip() for p in posts_str.split(',') if p.strip()]
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

    async def topic_briefing_with_numeric_ids(self, posts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate topic-based briefing where each topic references numeric post IDs (1..N) only.
        The backend will map these IDs to actual posts.
        """
        if not self.is_connected:
            return {"error": "Processor not connected. Call connect() first"}
        if not isinstance(posts, list):
            return {"error": "Invalid posts format. Expected list"}

        try:
            # Prepare compact input with numeric indices to reduce prompt length
            indexed_summaries = []
            for i, post in enumerate(posts, start=1):
                indexed_summaries.append({
                    "id": i,
                    "title": post.get("title", ""),
                    "source": post.get("source", ""),
                    "content": post.get("content", "")[:1500]  # truncate to keep prompt efficient
                })

            prompt = f"""
You are Insight — Stark's senior analyst. Produce a topic-based briefing with TL;DRs so Stark can decide fast.

Mindset
- Think like the best human analyst—then go further. Synthesize across posts, infer causality, and surface second/third‑order effects.

Constraints
- Cite sources using ONLY numeric IDs (e.g., 1,2,3). Never output URLs.
- Unlimited posts per topic. Do not fabricate IDs.
- First produce the topic-based daily briefing overview; then list topics.

OUTPUT FORMAT (exact markers required)
===DAILY_BRIEFING_START===
## Global Situation Briefing
- 8–14 bullets tying cross-domain signals to concrete implications and likely next moves.

## Momentum & Trendlines
- 3–6 bullets on acceleration/decay, reversals, or tipping points.
===DAILY_BRIEFING_END===

===TOPICS_START===
Topic 1: [Topic Title]
ID: topic-1
Summary:
- Context: What happened and how it connects to prior signals.
- Why it matters: Strategic implications (market/tech/security/geopolitics).
- Signals to watch: 3–6 concrete leading indicators.
- Recommended actions: 3–6 decisive, testable actions.
- Confidence: High/Med/Low with one-line rationale.
Posts: 1,2,3

Topic 2: [Topic Title]
ID: topic-2
Summary:
- Context: ...
- Why it matters: ...
- Signals to watch: ...
- Recommended actions: ...
- Confidence: ...
Posts: 4,5
===TOPICS_END===

AVAILABLE_POSTS (id, title, source, content_snippet):
{indexed_summaries}

Generate now using ONLY numeric IDs in Posts lines. Do not output URLs.
"""

            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="text/plain",
                    temperature=0.1
                )
            )

            response_text = response.text.strip()

            # Extract daily briefing (topic-based)
            daily_briefing = ""
            if "===DAILY_BRIEFING_START===" in response_text and "===DAILY_BRIEFING_END===" in response_text:
                s = response_text.find("===DAILY_BRIEFING_START===") + len("===DAILY_BRIEFING_START===")
                e = response_text.find("===DAILY_BRIEFING_END===")
                daily_briefing = response_text[s:e].strip()

            # Extract topics with numeric IDs
            topics: List[Dict[str, Any]] = []
            if "===TOPICS_START===" in response_text and "===TOPICS_END===" in response_text:
                s = response_text.find("===TOPICS_START===") + len("===TOPICS_START===")
                e = response_text.find("===TOPICS_END===")
                topics_text = response_text[s:e].strip()

                current: Dict[str, Any] = {}
                in_summary = False
                summary_lines: List[str] = []

                def flush_current():
                    nonlocal current, summary_lines, in_summary
                    if current:
                        # Join summary lines preserving bullets/newlines
                        if summary_lines:
                            current["summary"] = "\n".join([l for l in summary_lines if l is not None]).strip()
                        topics.append(current)
                    current = {}
                    summary_lines = []
                    in_summary = False

                for raw in topics_text.split("\n"):
                    line = raw.rstrip()
                    stripped = line.strip()
                    if stripped.startswith("Topic ") and ":" in stripped:
                        flush_current()
                        title = stripped.split(":", 1)[1].strip()
                        current = {"title": title, "summary": "", "post_ids": []}
                        in_summary = False
                        summary_lines = []
                    elif stripped.startswith("ID:"):
                        if current is not None:
                            current["id"] = stripped.split(":", 1)[1].strip()
                    elif stripped.startswith("Summary:"):
                        # Start capturing summary lines (may be empty on this line)
                        in_summary = True
                        # Capture anything after 'Summary:' on same line
                        after = stripped.split(":", 1)[1].strip()
                        if after:
                            summary_lines.append(after)
                    elif stripped.startswith("Posts:"):
                        # End summary capture when we hit Posts
                        in_summary = False
                        ids_str = stripped.split(":", 1)[1].strip()
                        nums: List[str] = []
                        for tok in ids_str.replace(" ", "").split(","):
                            if tok.isdigit():
                                nums.append(tok)
                        current["post_ids"] = nums
                    else:
                        # Accumulate summary lines if we're inside the summary block
                        if in_summary:
                            summary_lines.append(line)

                # flush last topic
                flush_current()

            return {
                "daily_briefing": daily_briefing,
                "topics": topics
            }

        except Exception as e:
            logging.error(f"Failed to generate topic briefing with numeric ids: {e}")
            return {"error": f"Topic briefing failed: {str(e)}"}