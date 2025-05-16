import requests
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Union
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor
import os

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

@dataclass
class NewsItem:
    """Data class for news items"""
    title: str
    content: str
    source: str
    timestamp: datetime
    url: str
    currency_pairs: List[str]

@dataclass
class SentimentResult:
    """Data class for sentiment analysis results"""
    news_id: str
    sentiment_score: float
    confidence: float
    currency_pairs: List[str]
    impact_level: str
    key_phrases: List[str]
    timestamp: datetime

class NewsSentimentAnalyzer:
    """
    A module for analyzing sentiment in Forex news and integrating with the Will system.
    This module fetches news from various sources, analyzes sentiment, and provides
    insights that can be used by the Will system for trading decisions.
    """

    def __init__(self, config: Dict[str, str]):
        """
        Initialize the NewsSentimentAnalyzer with configuration.

        Args:
            config (Dict[str, str]): Configuration dictionary containing API keys and endpoints
        """
        self.config = config
        self.api_key = config.get('NEWS_API_KEY')
        self.gemini_api_key = config.get('GEMINI_API_KEY')
        self.news_sources = config.get('NEWS_SOURCES', [])
        self.currency_pairs = config.get('CURRENCY_PAIRS', [])
        
        # Initialize cache for recent news items
        self.news_cache = {}
        self.sentiment_cache = {}
        
        # Initialize thread pool for parallel processing
        self.executor = ThreadPoolExecutor(max_workers=4)

    async def fetch_news(self, currency_pair: str = None) -> List[NewsItem]:
        """
        Fetch news items from configured sources.

        Args:
            currency_pair (str, optional): Specific currency pair to fetch news for

        Returns:
            List[NewsItem]: List of news items
        """
        try:
            # Example implementation using a news API
            headers = {'Authorization': f'Bearer {self.api_key}'}
            params = {
                'q': currency_pair if currency_pair else 'forex',
                'language': 'en',
                'sortBy': 'publishedAt'
            }
            
            response = requests.get(
                'https://newsapi.org/v2/everything',
                headers=headers,
                params=params
            )
            response.raise_for_status()
            
            news_data = response.json()
            news_items = []
            
            for article in news_data.get('articles', []):
                news_item = NewsItem(
                    title=article['title'],
                    content=article['description'],
                    source=article['source']['name'],
                    timestamp=datetime.fromisoformat(article['publishedAt'].replace('Z', '+00:00')),
                    url=article['url'],
                    currency_pairs=self._extract_currency_pairs(article['title'] + ' ' + article['description'])
                )
                news_items.append(news_item)
            
            return news_items
            
        except Exception as e:
            logger.error(f"Error fetching news: {str(e)}")
            return []

    def _extract_currency_pairs(self, text: str) -> List[str]:
        """
        Extract currency pairs from text.

        Args:
            text (str): Text to analyze

        Returns:
            List[str]: List of currency pairs found
        """
        # Simple implementation - can be enhanced with regex or ML
        found_pairs = []
        for pair in self.currency_pairs:
            if pair.replace('/', '') in text.replace(' ', ''):
                found_pairs.append(pair)
        return found_pairs

    async def analyze_sentiment(self, news_item: NewsItem) -> SentimentResult:
        """
        Analyze sentiment of a news item using Gemini API.

        Args:
            news_item (NewsItem): News item to analyze

        Returns:
            SentimentResult: Sentiment analysis result
        """
        try:
            # Prepare prompt for Gemini
            prompt = f"""
            Analyze the sentiment of the following Forex news:
            Title: {news_item.title}
            Content: {news_item.content}
            
            Provide a JSON response with:
            - sentiment_score (-1 to 1)
            - confidence (0 to 1)
            - impact_level (LOW, MEDIUM, HIGH)
            - key_phrases (list of important phrases)
            """

            # Call Gemini API
            headers = {
                'Authorization': f'Bearer {self.gemini_api_key}',
                'Content-Type': 'application/json'
            }
            
            response = requests.post(
                'https://api.gemini.com/v1/analyze',
                headers=headers,
                json={'prompt': prompt}
            )
            response.raise_for_status()
            
            result = response.json()
            
            return SentimentResult(
                news_id=news_item.url,
                sentiment_score=result['sentiment_score'],
                confidence=result['confidence'],
                currency_pairs=news_item.currency_pairs,
                impact_level=result['impact_level'],
                key_phrases=result['key_phrases'],
                timestamp=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"Error analyzing sentiment: {str(e)}")
            return None

    async def get_sentiment_insights(self, currency_pair: str = None) -> Dict[str, Union[float, List[SentimentResult]]]:
        """
        Get sentiment insights for a currency pair or all pairs.

        Args:
            currency_pair (str, optional): Specific currency pair to analyze

        Returns:
            Dict[str, Union[float, List[SentimentResult]]]: Sentiment insights
        """
        try:
            # Fetch news
            news_items = await self.fetch_news(currency_pair)
            
            # Analyze sentiment for each news item
            sentiment_results = []
            for news_item in news_items:
                result = await self.analyze_sentiment(news_item)
                if result:
                    sentiment_results.append(result)
            
            # Calculate aggregate sentiment
            if sentiment_results:
                avg_sentiment = sum(r.sentiment_score for r in sentiment_results) / len(sentiment_results)
                avg_confidence = sum(r.confidence for r in sentiment_results) / len(sentiment_results)
            else:
                avg_sentiment = 0.0
                avg_confidence = 0.0
            
            return {
                'average_sentiment': avg_sentiment,
                'average_confidence': avg_confidence,
                'results': sentiment_results
            }
            
        except Exception as e:
            logger.error(f"Error getting sentiment insights: {str(e)}")
            return {
                'average_sentiment': 0.0,
                'average_confidence': 0.0,
                'results': []
            }

    def cleanup(self):
        """Cleanup resources"""
        self.executor.shutdown() 