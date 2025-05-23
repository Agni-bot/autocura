# News Sentiment Analyzer Module

## Overview
The News Sentiment Analyzer is a module designed to enhance the Will system's trading decisions by analyzing sentiment in Forex news. It fetches news from various sources, analyzes the sentiment using the Gemini API, and provides insights that can be used to inform trading decisions.

## Features
- Real-time news fetching from multiple sources
- Sentiment analysis using Gemini API
- Currency pair extraction from news content
- Parallel processing for improved performance
- Caching mechanism for recent news and sentiment results
- Structured logging for monitoring and debugging

## Integration with Will System
The module integrates with the Will system through the following components:

1. **News Fetching**: Fetches relevant Forex news from configured sources
2. **Sentiment Analysis**: Analyzes news sentiment using Gemini API
3. **Insight Generation**: Provides aggregated sentiment insights for trading decisions

## Configuration
The module requires the following configuration parameters:

```python
config = {
    'NEWS_API_KEY': 'your_news_api_key',
    'GEMINI_API_KEY': 'your_gemini_api_key',
    'NEWS_SOURCES': ['Reuters', 'Bloomberg', 'Financial Times'],
    'CURRENCY_PAIRS': ['EUR/USD', 'GBP/USD', 'USD/JPY']
}
```

## API Endpoints
The module exposes the following endpoints:

1. **GET /api/will/news/sentiment**
   - Returns sentiment insights for all currency pairs
   - Query parameters:
     - `currency_pair` (optional): Specific currency pair to analyze

2. **GET /api/will/news/sentiment/{currency_pair}**
   - Returns sentiment insights for a specific currency pair

## Example Usage
```python
from news_sentiment_analyzer import NewsSentimentAnalyzer

# Initialize the analyzer
config = {
    'NEWS_API_KEY': 'your_news_api_key',
    'GEMINI_API_KEY': 'your_gemini_api_key',
    'NEWS_SOURCES': ['Reuters', 'Bloomberg'],
    'CURRENCY_PAIRS': ['EUR/USD', 'GBP/USD']
}
analyzer = NewsSentimentAnalyzer(config)

# Get sentiment insights
insights = await analyzer.get_sentiment_insights('EUR/USD')
print(f"Average Sentiment: {insights['average_sentiment']}")
print(f"Confidence: {insights['average_confidence']}")
```

## Testing
The module includes comprehensive tests in `tests/test_news_sentiment.py`. To run the tests:

```bash
pytest tests/test_news_sentiment.py -v
```

## Error Handling
The module implements robust error handling:
- API failures are logged and handled gracefully
- Missing or invalid configuration parameters are detected
- Network issues are handled with appropriate retries
- Invalid responses are logged and handled

## Performance Considerations
- Uses ThreadPoolExecutor for parallel processing
- Implements caching to reduce API calls
- Configurable number of workers for news fetching
- Efficient currency pair extraction

## Security
- API keys are managed securely through configuration
- All API calls are made over HTTPS
- Sensitive data is not logged
- Input validation is implemented for all public methods

## Monitoring
The module uses structured logging for monitoring:
- All API calls are logged
- Errors are logged with appropriate context
- Performance metrics are logged
- Cache hits/misses are tracked

## Future Enhancements
Planned improvements include:
1. Machine learning-based currency pair extraction
2. Enhanced sentiment analysis with multiple models
3. Real-time news alerts
4. Historical sentiment analysis
5. Integration with more news sources 