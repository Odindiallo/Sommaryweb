from crewai import Agent, Task, Crew
from bs4 import BeautifulSoup
import requests
import json
import os
from langchain_openai import ChatOpenAI
import cssutils
import re
from urllib.parse import urljoin
import base64
from PIL import Image
from io import BytesIO
import logging

cssutils.log.setLevel(logging.CRITICAL)

class WebsiteAnalyzer:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        self.llm = ChatOpenAI(
            model="gpt-3.5-turbo",
            temperature=0,
            api_key=os.getenv('OPENAI_API_KEY')
        )
        
        # Configure specialized agents
        self.style_analyzer = Agent(
            role='Web Design Analyst',
            goal='Analyze website design elements and styles',
            backstory="""You are an expert web designer who analyzes websites 
            to extract design patterns, colors, typography, and layout information.
            You provide detailed technical analysis of CSS and design elements.""",
            allow_delegation=False,
            verbose=False,
            llm=self.llm
        )
        
        self.structure_analyzer = Agent(
            role='HTML Structure Analyst',
            goal='Analyze website structure and components',
            backstory="""You are an expert in HTML and web architecture who analyzes
            website structure, semantic markup, and component organization.
            You provide detailed analysis of HTML patterns and best practices.""",
            allow_delegation=False,
            verbose=False,
            llm=self.llm
        )
        
        self.asset_collector = Agent(
            role='Asset Collector',
            goal='Collect and organize website assets',
            backstory="""You are responsible for identifying, downloading and
            organizing website assets including images, icons, and other media.
            You ensure proper organization and naming of assets.""",
            allow_delegation=False,
            verbose=False,
            llm=self.llm
        )

    def analyze_website(self, url):
        """Analyze a website and return comprehensive design analysis."""
        try:
            # Fetch website content
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Create tasks for analysis
            style_analysis_task = Task(
                description=f"Analyze the design elements of {url} including colors, typography, and spacing",
                agent=self.style_analyzer
            )
            
            structure_analysis_task = Task(
                description=f"Analyze the HTML structure and components of {url}",
                agent=self.structure_analyzer
            )
            
            asset_collection_task = Task(
                description=f"Identify and collect all assets from {url}",
                agent=self.asset_collector
            )
            
            # Create and run the crew
            crew = Crew(
                agents=[self.style_analyzer, self.structure_analyzer, self.asset_collector],
                tasks=[style_analysis_task, structure_analysis_task, asset_collection_task],
                verbose=True
            )
            
            # Get design elements
            colors = self._extract_colors(soup)
            fonts = self._extract_fonts(soup)
            spacing = self._extract_spacing(soup)
            layout = self._analyze_layout(soup)
            
            # Collect assets
            assets = self._collect_assets(soup, url)
            
            # Compile results
            analysis = {
                'url': url,
                'design_elements': {
                    'colors': colors,
                    'typography': fonts,
                    'spacing': spacing,
                    'layout': layout
                },
                'assets': assets,
                'structure': self._analyze_structure(soup)
            }
            
            return analysis
        except Exception as e:
            raise Exception(f"Error analyzing website: {str(e)}")
            
    def _extract_colors(self, soup):
        """Extract color codes from CSS and inline styles."""
        colors = set()
        
        # Extract from style tags
        for style in soup.find_all('style'):
            if style.string:
                sheet = cssutils.parseString(style.string)
                for rule in sheet:
                    if hasattr(rule, 'style'):
                        for property in rule.style:
                            if 'color' in property.name or 'background' in property.name:
                                colors.add(property.value)
        
        # Extract from inline styles
        for tag in soup.find_all(style=True):
            style = tag['style']
            color_matches = re.findall(r'#[0-9a-fA-F]{3,6}|rgb\([^)]+\)|rgba\([^)]+\)', style)
            colors.update(color_matches)
        
        return list(colors)
    
    def _extract_fonts(self, soup):
        """Extract font information from CSS."""
        fonts = set()
        
        for style in soup.find_all('style'):
            if style.string:
                sheet = cssutils.parseString(style.string)
                for rule in sheet:
                    if hasattr(rule, 'style'):
                        for property in rule.style:
                            if 'font' in property.name:
                                fonts.add(property.value)
        
        return list(fonts)
    
    def _extract_spacing(self, soup):
        """Extract spacing and alignment properties."""
        spacing = {
            'margins': set(),
            'padding': set(),
            'alignment': set()
        }
        
        for style in soup.find_all('style'):
            if style.string:
                sheet = cssutils.parseString(style.string)
                for rule in sheet:
                    if hasattr(rule, 'style'):
                        for property in rule.style:
                            if 'margin' in property.name:
                                spacing['margins'].add(property.value)
                            elif 'padding' in property.name:
                                spacing['padding'].add(property.value)
                            elif 'align' in property.name or 'justify' in property.name:
                                spacing['alignment'].add(property.value)
        
        return {k: list(v) for k, v in spacing.items()}
    
    def _analyze_layout(self, soup):
        """Analyze page layout structure."""
        layout = {
            'grid_usage': bool(soup.select('[class*="grid"]')),
            'flexbox_usage': bool(soup.select('[class*="flex"]')),
            'main_sections': [tag.name for tag in soup.find_all(['header', 'main', 'footer', 'nav', 'aside'])]
        }
        return layout
    
    def _collect_assets(self, soup, base_url):
        """Collect all media assets from the website."""
        assets = {
            'images': [],
            'icons': [],
            'backgrounds': []
        }
        
        # Collect images
        for img in soup.find_all('img'):
            src = img.get('src')
            if src:
                full_url = urljoin(base_url, src)
                assets['images'].append({
                    'url': full_url,
                    'alt': img.get('alt', ''),
                    'type': 'icon' if 'icon' in src.lower() or 'logo' in src.lower() else 'image'
                })
        
        # Collect background images from styles
        for tag in soup.find_all(style=True):
            style = tag['style']
            bg_matches = re.findall(r'background-image:\s*url\([\'"]?([^\'"]+)[\'"]?\)', style)
            for match in bg_matches:
                full_url = urljoin(base_url, match)
                assets['backgrounds'].append({
                    'url': full_url,
                    'element': tag.name
                })
        
        return assets
    
    def _analyze_structure(self, soup):
        """Analyze HTML structure and component organization."""
        structure = {
            'doctype': bool(soup.find('doctype')),
            'head_elements': [tag.name for tag in soup.head.children if tag.name],
            'semantic_elements': {
                tag: len(soup.find_all(tag)) 
                for tag in ['header', 'nav', 'main', 'article', 'section', 'aside', 'footer']
            },
            'meta_tags': len(soup.find_all('meta')),
            'scripts': len(soup.find_all('script')),
            'styles': len(soup.find_all('style')),
            'forms': len(soup.find_all('form'))
        }
        return structure
