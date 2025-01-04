import os
from crew import URLSummarizer
from dotenv import load_dotenv

def test_summarization():
    # Load environment variables from .env file
    load_dotenv()
    
    # Check for OpenAI API key
    if not os.getenv('OPENAI_API_KEY'):
        print("\nError: OPENAI_API_KEY environment variable is not set.")
        print("Please set your OpenAI API key using:")
        print("export OPENAI_API_KEY='your-api-key-here'")
        return False
    
    # Create an instance of URLSummarizer
    summarizer = URLSummarizer()
    
    # Test URL (using a stable, well-known website)
    test_url = "https://www.wikipedia.org"
    
    try:
        # Try to get a summary
        print("Attempting to summarize:", test_url)
        summary = summarizer.get_summary(test_url)
        
        print("\nSummary generated successfully!")
        print("-" * 50)
        print(summary)
        print("-" * 50)
        
        return True
    except Exception as e:
        print("\nError during summarization:")
        print(str(e))
        return False

if __name__ == "__main__":
    test_summarization()
