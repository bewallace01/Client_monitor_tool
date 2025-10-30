"""AI processor service with flexible provider support.

Provides AI-powered event classification and insight generation with support for:
- OpenAI (GPT-3.5, GPT-4)
- Anthropic (Claude)
- Mock (rule-based fallback)
"""

import json
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

from app.models.client import Client
from app.models.event import Event
from app.services.mock_api_service import MockAPIService

logger = logging.getLogger(__name__)


class AIProcessorService:
    """AI processing with flexible provider support."""

    # Provider constants
    PROVIDER_OPENAI = "openai"
    PROVIDER_ANTHROPIC = "anthropic"
    PROVIDER_MOCK = "mock"

    # Model defaults
    DEFAULT_OPENAI_MODEL = "gpt-3.5-turbo"
    DEFAULT_ANTHROPIC_MODEL = "claude-3-sonnet-20240229"

    @staticmethod
    async def classify_event(
        raw_data: Dict[str, Any],
        client: Client,
        crm_data: Optional[Dict[str, Any]] = None,
        provider: str = "openai",
        api_key: Optional[str] = None,
        model: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Classify raw search/news data into structured event.

        Args:
            raw_data: Raw data from search/news API
            client: Client model instance
            crm_data: Optional CRM enrichment data
            provider: AI provider (openai, anthropic, mock)
            api_key: API key for provider
            model: Specific model to use

        Returns:
            Dict with event classification data
        """
        # Validate provider
        if provider not in [AIProcessorService.PROVIDER_OPENAI, AIProcessorService.PROVIDER_ANTHROPIC, AIProcessorService.PROVIDER_MOCK]:
            logger.warning(f"Unknown AI provider: {provider}, falling back to mock")
            provider = AIProcessorService.PROVIDER_MOCK

        # Use mock if no API key provided (except for mock provider)
        if provider != AIProcessorService.PROVIDER_MOCK and not api_key:
            logger.warning(f"No API key provided for {provider}, using mock classification")
            provider = AIProcessorService.PROVIDER_MOCK

        try:
            if provider == AIProcessorService.PROVIDER_OPENAI:
                return await AIProcessorService._classify_with_openai(
                    raw_data, client, crm_data, api_key, model
                )
            elif provider == AIProcessorService.PROVIDER_ANTHROPIC:
                return await AIProcessorService._classify_with_anthropic(
                    raw_data, client, crm_data, api_key, model
                )
            else:  # mock
                return AIProcessorService._classify_with_mock(raw_data, client, crm_data)

        except Exception as e:
            logger.error(f"AI classification failed with {provider}: {str(e)}, falling back to mock")
            return AIProcessorService._classify_with_mock(raw_data, client, crm_data)

    @staticmethod
    async def generate_insights(
        event: Event,
        client: Client,
        crm_data: Optional[Dict[str, Any]] = None,
        provider: str = "openai",
        api_key: Optional[str] = None,
        model: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate actionable insights for an event.

        Args:
            event: Event model instance
            client: Client model instance
            crm_data: Optional CRM enrichment data
            provider: AI provider
            api_key: API key for provider
            model: Specific model to use

        Returns:
            Dict with insights and recommendations
        """
        # Validate provider
        if provider not in [AIProcessorService.PROVIDER_OPENAI, AIProcessorService.PROVIDER_ANTHROPIC, AIProcessorService.PROVIDER_MOCK]:
            logger.warning(f"Unknown AI provider: {provider}, falling back to mock")
            provider = AIProcessorService.PROVIDER_MOCK

        # Use mock if no API key provided
        if provider != AIProcessorService.PROVIDER_MOCK and not api_key:
            logger.warning(f"No API key provided for {provider}, using mock insights")
            provider = AIProcessorService.PROVIDER_MOCK

        try:
            if provider == AIProcessorService.PROVIDER_OPENAI:
                return await AIProcessorService._generate_insights_openai(
                    event, client, crm_data, api_key, model
                )
            elif provider == AIProcessorService.PROVIDER_ANTHROPIC:
                return await AIProcessorService._generate_insights_anthropic(
                    event, client, crm_data, api_key, model
                )
            else:  # mock
                return AIProcessorService._generate_insights_mock(event, client, crm_data)

        except Exception as e:
            logger.error(f"AI insight generation failed with {provider}: {str(e)}, falling back to mock")
            return AIProcessorService._generate_insights_mock(event, client, crm_data)

    # ==================== OpenAI Implementation ====================

    @staticmethod
    async def _classify_with_openai(
        raw_data: Dict[str, Any],
        client: Client,
        crm_data: Optional[Dict[str, Any]],
        api_key: str,
        model: Optional[str]
    ) -> Dict[str, Any]:
        """Classify event using OpenAI."""
        try:
            from openai import AsyncOpenAI
        except ImportError:
            logger.error("OpenAI library not installed, falling back to mock")
            return AIProcessorService._classify_with_mock(raw_data, client, crm_data)

        if not model:
            model = AIProcessorService.DEFAULT_OPENAI_MODEL

        # Build classification prompt
        prompt = AIProcessorService._build_classification_prompt(raw_data, client, crm_data)

        try:
            openai_client = AsyncOpenAI(api_key=api_key)

            response = await openai_client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an AI assistant that classifies business news and events. Respond only with valid JSON."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,
                max_tokens=500,
                response_format={"type": "json_object"}
            )

            result_text = response.choices[0].message.content
            classification = json.loads(result_text)

            logger.info(f"OpenAI classification successful for {client.name}")
            return classification

        except Exception as e:
            logger.error(f"OpenAI API error: {str(e)}")
            raise

    @staticmethod
    async def _generate_insights_openai(
        event: Event,
        client: Client,
        crm_data: Optional[Dict[str, Any]],
        api_key: str,
        model: Optional[str]
    ) -> Dict[str, Any]:
        """Generate insights using OpenAI."""
        try:
            from openai import AsyncOpenAI
        except ImportError:
            logger.error("OpenAI library not installed, falling back to mock")
            return AIProcessorService._generate_insights_mock(event, client, crm_data)

        if not model:
            model = AIProcessorService.DEFAULT_OPENAI_MODEL

        # Build insights prompt
        prompt = AIProcessorService._build_insights_prompt(event, client, crm_data)

        try:
            openai_client = AsyncOpenAI(api_key=api_key)

            response = await openai_client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a customer success AI assistant that provides actionable insights and recommendations. Respond only with valid JSON."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.5,
                max_tokens=800,
                response_format={"type": "json_object"}
            )

            result_text = response.choices[0].message.content
            insights = json.loads(result_text)

            logger.info(f"OpenAI insights generated for event {event.id}")
            return insights

        except Exception as e:
            logger.error(f"OpenAI API error: {str(e)}")
            raise

    # ==================== Anthropic Implementation ====================

    @staticmethod
    async def _classify_with_anthropic(
        raw_data: Dict[str, Any],
        client: Client,
        crm_data: Optional[Dict[str, Any]],
        api_key: str,
        model: Optional[str]
    ) -> Dict[str, Any]:
        """Classify event using Anthropic Claude."""
        try:
            from anthropic import AsyncAnthropic
        except ImportError:
            logger.error("Anthropic library not installed, falling back to mock")
            return AIProcessorService._classify_with_mock(raw_data, client, crm_data)

        if not model:
            model = AIProcessorService.DEFAULT_ANTHROPIC_MODEL

        # Build classification prompt
        prompt = AIProcessorService._build_classification_prompt(raw_data, client, crm_data)

        try:
            anthropic_client = AsyncAnthropic(api_key=api_key)

            response = await anthropic_client.messages.create(
                model=model,
                max_tokens=1000,
                temperature=0.3,
                messages=[
                    {
                        "role": "user",
                        "content": f"{prompt}\n\nRespond only with valid JSON."
                    }
                ]
            )

            result_text = response.content[0].text
            classification = json.loads(result_text)

            logger.info(f"Anthropic classification successful for {client.name}")
            return classification

        except Exception as e:
            logger.error(f"Anthropic API error: {str(e)}")
            raise

    @staticmethod
    async def _generate_insights_anthropic(
        event: Event,
        client: Client,
        crm_data: Optional[Dict[str, Any]],
        api_key: str,
        model: Optional[str]
    ) -> Dict[str, Any]:
        """Generate insights using Anthropic Claude."""
        try:
            from anthropic import AsyncAnthropic
        except ImportError:
            logger.error("Anthropic library not installed, falling back to mock")
            return AIProcessorService._generate_insights_mock(event, client, crm_data)

        if not model:
            model = AIProcessorService.DEFAULT_ANTHROPIC_MODEL

        # Build insights prompt
        prompt = AIProcessorService._build_insights_prompt(event, client, crm_data)

        try:
            anthropic_client = AsyncAnthropic(api_key=api_key)

            response = await anthropic_client.messages.create(
                model=model,
                max_tokens=1500,
                temperature=0.5,
                messages=[
                    {
                        "role": "user",
                        "content": f"{prompt}\n\nRespond only with valid JSON."
                    }
                ]
            )

            result_text = response.content[0].text
            insights = json.loads(result_text)

            logger.info(f"Anthropic insights generated for event {event.id}")
            return insights

        except Exception as e:
            logger.error(f"Anthropic API error: {str(e)}")
            raise

    # ==================== Mock Implementation ====================

    @staticmethod
    def _classify_with_mock(
        raw_data: Dict[str, Any],
        client: Client,
        crm_data: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Classify event using mock/rule-based logic."""
        return MockAPIService.mock_ai_classification(raw_data, client.name)

    @staticmethod
    def _generate_insights_mock(
        event: Event,
        client: Client,
        crm_data: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate insights using mock logic."""
        event_data = {
            "title": event.title,
            "category": event.category,
            "relevance_score": event.relevance_score,
            "sentiment_score": event.sentiment_score
        }
        return MockAPIService.mock_ai_insights(event_data, crm_data)

    # ==================== Prompt Builders ====================

    @staticmethod
    def _build_classification_prompt(
        raw_data: Dict[str, Any],
        client: Client,
        crm_data: Optional[Dict[str, Any]]
    ) -> str:
        """Build prompt for event classification."""
        # Extract content from raw data
        content = ""
        if "items" in raw_data:  # Google Search format (raw)
            items = raw_data.get("items", [])
            if items:
                content = f"Title: {items[0].get('title', '')}\n"
                content += f"Snippet: {items[0].get('snippet', '')}\n"
                content += f"URL: {items[0].get('link', '')}"
        elif "articles" in raw_data:  # NewsAPI format (raw)
            articles = raw_data.get("articles", [])
            if articles:
                content = f"Title: {articles[0].get('title', '')}\n"
                content += f"Description: {articles[0].get('description', '')}\n"
                content += f"Source: {articles[0].get('source', {}).get('name', '')}"
        elif "title" in raw_data:  # Normalized format (from extract_results_for_storage)
            content = f"Title: {raw_data.get('title', '')}\n"
            content += f"Description: {raw_data.get('description', '') or raw_data.get('content', '')}\n"
            content += f"URL: {raw_data.get('url', '')}\n"
            content += f"Source: {raw_data.get('source', '')}"

        # Build context
        context = f"Client Name: {client.name}\n"
        if client.industry:
            context += f"Industry: {client.industry}\n"

        # Add CRM context if available
        if crm_data and crm_data.get("success"):
            context += f"\nCRM Data:\n"
            if crm_data.get("health_score"):
                context += f"- Health Score: {crm_data['health_score']}\n"
            if crm_data.get("annual_revenue"):
                context += f"- Annual Revenue: ${crm_data['annual_revenue']:,}\n"
            if crm_data.get("lifecycle_stage"):
                context += f"- Lifecycle Stage: {crm_data['lifecycle_stage']}\n"

        prompt = f"""Classify the following business event about {client.name}.

{context}

Event Content:
{content}

Analyze this event and provide a JSON response with the following structure:
{{
  "title": "Clear, concise title (max 200 chars)",
  "description": "Detailed description (max 1000 chars)",
  "category": "One of: funding, acquisition, leadership_change, product_launch, partnership, financial_results, award, regulatory, expansion, other",
  "subcategory": "More specific category if applicable, or null",
  "relevance_score": "Float 0.0-1.0 indicating relevance to customer success monitoring",
  "sentiment_score": "Float -1.0 to 1.0 indicating sentiment (negative to positive)",
  "confidence_score": "Float 0.0-1.0 indicating classification confidence",
  "event_date": "ISO datetime string or null if unknown",
  "tags": ["array", "of", "relevant", "tags"]
}}

Guidelines:
- relevance_score: 0.8-1.0 for major events (funding, acquisition), 0.5-0.8 for moderate (partnerships, launches), 0.0-0.5 for minor
- sentiment_score: Consider impact on business relationship (positive growth signals = positive, challenges = negative)
- Be conservative with confidence_score if information is limited"""

        return prompt

    @staticmethod
    def _build_insights_prompt(
        event: Event,
        client: Client,
        crm_data: Optional[Dict[str, Any]]
    ) -> str:
        """Build prompt for insight generation."""
        # Build context
        context = f"""Client: {client.name}
Event Category: {event.category}
Relevance Score: {event.relevance_score}
Sentiment Score: {event.sentiment_score}
"""

        if client.industry:
            context += f"Industry: {client.industry}\n"

        # Add CRM context
        if crm_data and crm_data.get("success"):
            context += f"\nCRM Intelligence:\n"
            health_score = crm_data.get("health_score")
            if health_score:
                status = "Healthy" if health_score >= 70 else "At Risk" if health_score >= 50 else "Critical"
                context += f"- Account Health: {health_score}/100 ({status})\n"
            if crm_data.get("annual_revenue"):
                context += f"- Annual Revenue: {crm_data.get('annual_revenue_formatted', 'N/A')}\n"
            if crm_data.get("lifecycle_stage"):
                context += f"- Lifecycle Stage: {crm_data['lifecycle_stage']}\n"
            if crm_data.get("open_opportunities"):
                context += f"- Open Opportunities: {crm_data['open_opportunities']}\n"
            if crm_data.get("open_cases"):
                context += f"- Open Support Cases: {crm_data['open_cases']}\n"

            # Contract info
            contract_end = crm_data.get("contract_end_date")
            if contract_end:
                context += f"- Contract End Date: {contract_end}\n"

        # Event details
        event_info = f"""
Event Title: {event.title}
Event Description: {event.description or 'N/A'}
Event URL: {event.url or 'N/A'}
"""

        prompt = f"""You are a customer success AI assistant. Analyze this event and provide actionable insights and recommendations.

{context}

{event_info}

Provide a JSON response with this structure:
{{
  "insights": ["Array of 2-5 key insights about what this event means for the customer relationship"],
  "recommended_actions": ["Array of 2-5 specific, actionable recommendations for the customer success team"],
  "risk_assessment": "One of: Low Risk, Medium Risk, High Risk, Critical",
  "urgency_level": "One of: Low, Normal, High, Critical",
  "talking_points": ["Array of 2-4 conversation starters for customer outreach"]
}}

Guidelines:
- Focus on customer success implications
- Consider the CRM context (health score, opportunities, cases)
- Prioritize actions that strengthen the relationship
- Be specific and actionable (avoid generic advice)
- Escalate urgency if account health is poor or contract renewal is near"""

        return prompt
