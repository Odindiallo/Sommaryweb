from crewai import Agent, Task, Crew
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import os
from langchain_openai import ChatOpenAI
import re

# Load environment variables
load_dotenv()

class URLSummarizer:
    def __init__(self):
        """Initialize the URL summarizer."""
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        # Initialize OpenAI chat model
        self.llm = ChatOpenAI(
            model="gpt-3.5-turbo",
            temperature=0,
            api_key=os.getenv('OPENAI_API_KEY')
        )
        
        # Configure the summarizer agent
        self.summarizer = Agent(
            role='Technical Writer',
            goal='Create detailed technical documentation',
            backstory="""You are a technical writer who creates clear, factual documentation.
            You focus on technical details and implementation.
            You use neutral, professional language without marketing speak.
            You never use promotional phrases or future-focused statements.""",
            allow_delegation=False,
            verbose=False,
            llm=self.llm
        )

    def _fetch_url_content(self, url):
        """Fetch and clean content from a URL."""
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Remove script, style, and nav elements
            for element in soup(['script', 'style', 'nav', 'header', 'footer']):
                element.decompose()
            
            # Get main content
            main_content = soup.find('main') or soup.find('article') or soup.find('body')
            if main_content:
                text = main_content.get_text()
            else:
                text = soup.get_text()
            
            # Clean up text
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)
            
            return text
        except Exception as e:
            raise Exception(f"Error fetching URL content: {str(e)}")

    def _clean_summary(self, text):
        """Clean up the summary text by removing AI-generated prefixes and formatting."""
        # Remove common AI response prefixes
        prefixes_to_remove = [
            r"^Summary:",
            r"^I will create a comprehensive summary of the content provided\.",
            r"^Here's a comprehensive summary:",
            r"^Final Answer:",
            r"^Thought:",
            r"^Let me summarize this content for you:",
            r"^Unfortunately, there was an error.*?I will proceed with",
            r"^Error:.*$",
            r"^The content has been summarized\.",
            r"^Here is a summary of the content:",
            r"^Let me provide a summary of the content:",
            r"^Based on the content provided,",
            r"^After analyzing the content,",
            r"^\[I do not need to use a tool for this task\.\]",
            r"^\[I do not need to use a tool\]",
        ]
        
        cleaned_text = text
        for prefix in prefixes_to_remove:
            cleaned_text = re.sub(prefix, "", cleaned_text, flags=re.IGNORECASE | re.MULTILINE).strip()
        
        # Remove extra whitespace and normalize line breaks
        cleaned_text = re.sub(r'\s+', ' ', cleaned_text).strip()
        
        return cleaned_text

    def create_crew(self, url):
        """Create a crew for content summarization."""
        # Create tasks
        content = self._fetch_url_content(url)
        
        summarize_task = Task(
            description=f"""Write a direct blog post about this content. Critical requirements:

            1. DO NOT include any meta-commentary or tool-related comments
            2. Start with a clear title using "# Title"
            3. Structure the content with proper sections:
               - Introduction (2-3 paragraphs)
               - Key Features/Main Points (use ## headings)
               - Benefits and Use Cases
               - Technical Details (if relevant)
               - Conclusion
            
            4. Use markdown formatting:
               - ## for section headings
               - ### for subsections
               - **bold** for emphasis
               - - bullet points for lists
               - > for important quotes
            
            5. Writing style:
               - Professional and engaging
               - Clear explanations
               - Use examples where helpful
               - Include technical details
            
            6. Length: Aim for 800-1200 words
            
            Content to analyze:
            {content[:4000]}...""",
            agent=self.summarizer
        )

        # Create the crew
        crew = Crew(
            agents=[self.summarizer],
            tasks=[summarize_task],
            verbose=False
        )

        return crew

    def get_summary(self, url: str) -> str:
        """Get a summary of the content at the given URL."""
        try:
            content = self._fetch_url_content(url)
            
            # Create a task with a very strict template
            summarize_task = Task(
                description=f"""Write a technical summary of the content. Do not include any meta text like 'I will start writing' or 'Article Summary'.
Start directly with a # heading for the title. Example:

# Machine Learning Fundamentals

## Overview
Machine learning is a branch of artificial intelligence...

## Key Components
- Neural Networks: Core building blocks...
- Training Data: Essential input for...
- Algorithms: Mathematical approaches...

Now write your summary for this content:
{content[:4000]}...""",
                agent=self.summarizer
            )

            crew = Crew(
                agents=[self.summarizer],
                tasks=[summarize_task],
                verbose=False
            )

            result = crew.kickoff()
            
            # Clean up the result
            if not result or not result.strip():
                raise Exception("Empty response from AI")
                
            # Remove any meta-commentary
            lines = result.split('\n')
            content_lines = []
            started = False
            
            for line in lines:
                # Skip meta text lines
                if any(skip in line.lower() for skip in [
                    'i will', 'article summary', 'technical documentation',
                    'following', 'structure', 'example', 'provided'
                ]):
                    continue
                    
                # Skip empty lines at start
                if not started and not line.strip():
                    continue
                    
                # Start capturing when we see a heading
                if line.startswith('#'):
                    started = True
                    
                # Once started, include all lines
                if started:
                    content_lines.append(line)
            
            # If we haven't found any content, try to find the first real line
            if not content_lines:
                content_lines = [line for line in lines 
                               if line.strip() and 
                               not line.startswith('[') and
                               not any(skip in line.lower() for skip in [
                                   'i will', 'article summary', 'technical documentation',
                                   'following', 'structure', 'example', 'provided'
                               ])]
                
            if not content_lines:
                raise Exception("No valid content found in the response")
                
            # Ensure first line is a title
            if not content_lines[0].startswith('#'):
                content_lines[0] = f"# {content_lines[0]}"
            
            cleaned_result = '\n'.join(content_lines).strip()
            
            # Validate the result
            if len(cleaned_result) < 100:  # Arbitrary minimum length
                raise Exception("Generated content is too short")
                
            return cleaned_result
            
        except Exception as e:
            print(f"Error in get_summary: {str(e)}")  # Add logging
            print(f"Raw result: {result if 'result' in locals() else 'No result'}")  # Add logging
            raise Exception(f"Failed to generate summary: {str(e)}")
