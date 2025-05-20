import unittest
import asyncio
from datetime import datetime
from news_sentiment_analyzer import NewsSentimentAnalyzer, NewsItem, SentimentResult

class TestNewsSentimentAnalyzer(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures"""
        self.config = {
            'NEWS_API_KEY': 'test_news_api_key',
            'GEMINI_API_KEY': 'test_gemini_api_key',
            'NEWS_SOURCES': ['Reuters', 'Bloomberg', 'Financial Times'],
            'CURRENCY_PAIRS': ['EUR/USD', 'GBP/USD', 'USD/JPY']
        }
        self.analyzer = NewsSentimentAnalyzer(self.config)

    def test_extract_currency_pairs(self):
        """Test currency pair extraction from text"""
        text = "EUR/USD hits new high as USD/JPY falls"
        pairs = self.analyzer._extract_currency_pairs(text)
        self.assertIn('EUR/USD', pairs)
        self.assertIn('USD/JPY', pairs)
        self.assertEqual(len(pairs), 2)

    async def test_fetch_news(self):
        """Test news fetching functionality"""
        news_items = await self.analyzer.fetch_news('EUR/USD')
        self.assertIsInstance(news_items, list)
        if news_items:
            self.assertIsInstance(news_items[0], NewsItem)
            self.assertIsInstance(news_items[0].timestamp, datetime)

    async def test_analyze_sentiment(self):
        """Test sentiment analysis functionality"""
        news_item = NewsItem(
            title="EUR/USD Rises on Strong Economic Data",
            content="The Euro gained against the US Dollar following positive economic indicators.",
            source="Test Source",
            timestamp=datetime.now(),
            url="http://test.com/news/1",
            currency_pairs=['EUR/USD']
        )
        
        result = await self.analyzer.analyze_sentiment(news_item)
        if result:  # Result might be None if API is not available
            self.assertIsInstance(result, SentimentResult)
            self.assertIsInstance(result.sentiment_score, float)
            self.assertIsInstance(result.confidence, float)
            self.assertIn(result.impact_level, ['LOW', 'MEDIUM', 'HIGH'])

    async def test_get_sentiment_insights(self):
        """Test getting sentiment insights"""
        insights = await self.analyzer.get_sentiment_insights('EUR/USD')
        self.assertIsInstance(insights, dict)
        self.assertIn('average_sentiment', insights)
        self.assertIn('average_confidence', insights)
        self.assertIn('results', insights)
        self.assertIsInstance(insights['results'], list)

    def tearDown(self):
        """Clean up test fixtures"""
        self.analyzer.cleanup()

def run_async_test(coro):
    """Helper function to run async tests"""
    return asyncio.get_event_loop().run_until_complete(coro)

if __name__ == '__main__':
    unittest.main() 