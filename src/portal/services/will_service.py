import requests
import json
import logging
from typing import Dict, Optional, Union
from datetime import datetime
from .config import settings

logger = logging.getLogger(__name__)

class WillService:
    """
    Service for interacting with the Will Trading System.
    Handles all communication between the portal and Will's API endpoints.
    """

    def __init__(self, will_api_url: str = None):
        """
        Initialize the Will service.

        Args:
            will_api_url (str): Base URL for the Will API
        """
        self.base_url = (will_api_url or settings.WILL_API_URL).rstrip('/')
        self.session = requests.Session()

    def get_system_status(self) -> Dict:
        """
        Get the current status of the Will system.

        Returns:
            Dict: System status information
        """
        try:
            response = self.session.get(f"{self.base_url}/api/will/status")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error getting Will system status: {str(e)}")
            return {
                "error": "Failed to get system status",
                "details": str(e)
            }

    def get_trading_decision(self, asset: str, volume: float) -> Dict:
        """
        Get a trading decision from Will for a specific asset.

        Args:
            asset (str): The trading asset (e.g., "EUR/USD")
            volume (float): The requested trading volume

        Returns:
            Dict: Trading decision information
        """
        try:
            payload = {
                "asset": asset,
                "requested_volume": volume,
                "timestamp": datetime.now().isoformat()
            }
            
            response = self.session.post(
                f"{self.base_url}/api/will/decision",
                json=payload
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error getting trading decision: {str(e)}")
            return {
                "error": "Failed to get trading decision",
                "details": str(e)
            }

    def get_news_sentiment(self, currency_pair: Optional[str] = None) -> Dict:
        """
        Get sentiment analysis for news related to currency pairs.

        Args:
            currency_pair (str, optional): Specific currency pair to analyze

        Returns:
            Dict: Sentiment analysis results
        """
        try:
            url = f"{self.base_url}/api/will/news/sentiment"
            if currency_pair:
                url = f"{url}/{currency_pair}"
            
            response = self.session.get(url)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error getting news sentiment: {str(e)}")
            return {
                "error": "Failed to get news sentiment",
                "details": str(e)
            }

    def get_combined_analysis(self, asset: str) -> Dict:
        """
        Get a combined analysis including system status, trading decision,
        and news sentiment for a specific asset.

        Args:
            asset (str): The trading asset to analyze

        Returns:
            Dict: Combined analysis results
        """
        try:
            # Get all relevant data
            status = self.get_system_status()
            decision = self.get_trading_decision(asset, 10000)  # Default volume
            sentiment = self.get_news_sentiment(asset)

            # Combine the results
            return {
                "timestamp": datetime.now().isoformat(),
                "asset": asset,
                "system_status": status,
                "trading_decision": decision,
                "news_sentiment": sentiment,
                "analysis_summary": self._generate_summary(status, decision, sentiment)
            }
        except Exception as e:
            logger.error(f"Error getting combined analysis: {str(e)}")
            return {
                "error": "Failed to get combined analysis",
                "details": str(e)
            }

    def _generate_summary(self, status: Dict, decision: Dict, sentiment: Dict) -> str:
        """
        Generate a human-readable summary of the analysis.

        Args:
            status (Dict): System status
            decision (Dict): Trading decision
            sentiment (Dict): News sentiment

        Returns:
            str: Summary text
        """
        try:
            summary_parts = []
            
            # System status summary
            if status.get("status") == "OPERATIONAL":
                summary_parts.append("System is operational and ready for trading.")
            
            # Trading decision summary
            if "trade_signal" in decision:
                signal = decision["trade_signal"]
                confidence = decision.get("confidence_score", 0)
                summary_parts.append(
                    f"Trading signal: {signal} with {confidence:.0%} confidence."
                )
            
            # Sentiment summary
            if "sentiment_analysis" in sentiment:
                avg_sentiment = sentiment["sentiment_analysis"].get("average_sentiment", 0)
                sentiment_level = "positive" if avg_sentiment > 0 else "negative" if avg_sentiment < 0 else "neutral"
                summary_parts.append(f"News sentiment is {sentiment_level}.")
            
            return " ".join(summary_parts)
        except Exception as e:
            logger.error(f"Error generating summary: {str(e)}")
            return "Unable to generate analysis summary." 