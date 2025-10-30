"""Unified CRM service supporting multiple providers.

This service provides a single interface for CRM operations that routes to the
appropriate provider (Salesforce, HubSpot, Mock) based on business configuration.
"""

import logging
from typing import Dict, Any, Optional
from uuid import UUID
from sqlalchemy.orm import Session

from app.models.client import Client
from app.models.api_config import APIConfig
from app.schemas.api_config import APIProvider
from app.services.salesforce_service import SalesforceService
from app.services.mock_api_service import MockAPIService

logger = logging.getLogger(__name__)


class CRMService:
    """Unified CRM interface supporting multiple providers."""

    @staticmethod
    async def enrich_client(
        db: Session,
        business_id: UUID,
        client: Client,
        force_mock: bool = False
    ) -> Dict[str, Any]:
        """
        Enrich client with CRM data from configured provider.

        Args:
            db: Database session
            business_id: Business UUID
            client: Client model instance
            force_mock: Force use of mock data (for testing)

        Returns:
            Dict with standardized CRM enrichment data
        """
        if force_mock:
            logger.info(f"Using mock CRM data for client: {client.name}")
            return CRMService._standardize_mock_data(
                MockAPIService.mock_crm_data(client.id, client.name),
                "mock"
            )

        # Get CRM API configuration for business
        crm_config = CRMService._get_crm_config(db, business_id)

        if not crm_config:
            logger.info(f"No CRM API configured for business {business_id}, using mock data")
            return CRMService._standardize_mock_data(
                MockAPIService.mock_crm_data(client.id, client.name),
                "mock"
            )

        # Route to appropriate provider
        provider = crm_config.provider

        try:
            if provider == APIProvider.SALESFORCE:
                return await CRMService._enrich_from_salesforce(crm_config, client)
            elif provider == APIProvider.HUBSPOT:
                return await CRMService._enrich_from_hubspot(crm_config, client)
            else:
                logger.warning(f"Unsupported CRM provider: {provider}, using mock data")
                return CRMService._standardize_mock_data(
                    MockAPIService.mock_crm_data(client.id, client.name),
                    provider
                )

        except Exception as e:
            logger.error(f"CRM enrichment failed for {client.name}: {str(e)}, falling back to mock data")
            return CRMService._standardize_mock_data(
                MockAPIService.mock_crm_data(client.id, client.name),
                f"{provider}_error"
            )

    @staticmethod
    def _get_crm_config(db: Session, business_id: UUID) -> Optional[APIConfig]:
        """Get active CRM API configuration for a business."""
        crm_providers = [APIProvider.SALESFORCE, APIProvider.HUBSPOT]

        return db.query(APIConfig).filter(
            APIConfig.business_id == business_id,
            APIConfig.provider.in_(crm_providers),
            APIConfig.is_active == True
        ).first()

    @staticmethod
    async def _enrich_from_salesforce(
        config: APIConfig,
        client: Client
    ) -> Dict[str, Any]:
        """Enrich client from Salesforce."""
        logger.info(f"Enriching client {client.name} from Salesforce")

        # Authenticate with Salesforce
        auth_result = await SalesforceService.authenticate(
            client_id=config.api_key,  # Stored as api_key
            client_secret=config.api_secret,  # Stored as api_secret
            refresh_token=config.refresh_token
        )

        # Get enriched data
        enrichment = await SalesforceService.get_enriched_account_data(
            access_token=auth_result["access_token"],
            instance_url=auth_result["instance_url"],
            client=client
        )

        return CRMService._standardize_crm_data(enrichment, "salesforce")

    @staticmethod
    async def _enrich_from_hubspot(
        config: APIConfig,
        client: Client
    ) -> Dict[str, Any]:
        """
        Enrich client from HubSpot.

        Note: HubSpot integration to be implemented. For now, returns mock data.
        """
        logger.warning("HubSpot CRM integration not yet implemented, using mock data")
        return CRMService._standardize_mock_data(
            MockAPIService.mock_crm_data(client.id, client.name),
            "hubspot_todo"
        )

    @staticmethod
    def _standardize_crm_data(raw_data: Dict[str, Any], source: str) -> Dict[str, Any]:
        """
        Standardize CRM data from any provider into common format.

        Args:
            raw_data: Raw CRM data from provider
            source: Source provider name

        Returns:
            Standardized CRM data dict
        """
        if not raw_data.get("found", False):
            return {
                "success": False,
                "source": source,
                "message": raw_data.get("message", "Account not found"),
                "error": raw_data.get("error")
            }

        # Already standardized from Salesforce service
        if source == "salesforce":
            return {
                "success": True,
                **raw_data
            }

        # Add standardization for other providers here
        return {
            "success": True,
            "source": source,
            **raw_data
        }

    @staticmethod
    def _standardize_mock_data(mock_data: Dict[str, Any], source: str) -> Dict[str, Any]:
        """Standardize mock CRM data."""
        return {
            "success": True,
            "found": True,
            "source": source,
            "is_mock": True,
            **mock_data
        }

    @staticmethod
    def extract_health_score(crm_data: Dict[str, Any]) -> Optional[float]:
        """Extract health score from CRM data."""
        if not crm_data.get("success"):
            return None
        return crm_data.get("health_score")

    @staticmethod
    def extract_annual_revenue(crm_data: Dict[str, Any]) -> Optional[float]:
        """Extract annual revenue from CRM data."""
        if not crm_data.get("success"):
            return None
        return crm_data.get("annual_revenue")

    @staticmethod
    def extract_primary_contact(crm_data: Dict[str, Any]) -> Optional[Dict[str, str]]:
        """Extract primary contact from CRM data."""
        if not crm_data.get("success"):
            return None

        contacts = crm_data.get("contacts", [])
        for contact in contacts:
            if contact.get("is_primary"):
                return contact

        # Return first contact if no primary
        return contacts[0] if contacts else None

    @staticmethod
    def calculate_engagement_score(crm_data: Dict[str, Any]) -> float:
        """
        Calculate engagement score based on CRM data.

        Returns a score from 0.0 to 1.0 based on:
        - Open opportunities
        - Open cases
        - Recent interactions
        - Health score

        Args:
            crm_data: Standardized CRM data

        Returns:
            Engagement score (0.0-1.0)
        """
        if not crm_data.get("success"):
            return 0.5  # Neutral score if no CRM data

        score = 0.5  # Start neutral

        # Health score contribution (40% weight)
        health_score = crm_data.get("health_score")
        if health_score is not None:
            score += (health_score / 100 - 0.5) * 0.4

        # Opportunities contribution (30% weight)
        open_opps = crm_data.get("open_opportunities", 0)
        if open_opps > 0:
            score += min(open_opps / 5, 1.0) * 0.3

        # Cases contribution (negative 20% weight)
        open_cases = crm_data.get("open_cases", 0)
        if open_cases > 0:
            score -= min(open_cases / 10, 1.0) * 0.2

        # NPS contribution (10% weight)
        nps_score = crm_data.get("nps_score")
        if nps_score is not None:
            # NPS is typically 0-10, normalize to 0-1
            score += (nps_score / 10 - 0.5) * 0.1

        # Clamp to 0-1 range
        return max(0.0, min(1.0, score))

    @staticmethod
    def is_at_risk(crm_data: Dict[str, Any]) -> bool:
        """
        Determine if account is at risk based on CRM data.

        Args:
            crm_data: Standardized CRM data

        Returns:
            True if account appears at risk
        """
        if not crm_data.get("success"):
            return False

        # Check health score
        health_score = crm_data.get("health_score")
        if health_score and health_score < 50:
            return True

        # Check churn risk
        churn_risk = crm_data.get("churn_risk")
        if churn_risk and churn_risk > 0.3:  # 30% churn risk
            return True

        # Check lifecycle stage
        lifecycle = crm_data.get("lifecycle_stage", "").lower()
        if "at risk" in lifecycle or "churn" in lifecycle:
            return True

        # Check case-to-opportunity ratio
        open_cases = crm_data.get("open_cases", 0)
        open_opps = crm_data.get("open_opportunities", 0)
        if open_cases > 3 and open_opps == 0:
            return True

        return False

    @staticmethod
    def get_contract_status(crm_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get contract status information from CRM data.

        Args:
            crm_data: Standardized CRM data

        Returns:
            Dict with contract status information
        """
        if not crm_data.get("success"):
            return {
                "has_contract_data": False
            }

        contract_end = crm_data.get("contract_end_date")
        if not contract_end:
            return {
                "has_contract_data": False
            }

        try:
            from datetime import datetime
            end_date = datetime.fromisoformat(contract_end.replace("Z", "+00:00"))
            now = datetime.utcnow()
            days_until_end = (end_date - now).days

            return {
                "has_contract_data": True,
                "contract_end_date": contract_end,
                "days_until_end": days_until_end,
                "is_renewal_upcoming": days_until_end <= 90,
                "is_renewal_urgent": days_until_end <= 30,
                "status": "expiring_soon" if days_until_end <= 30 else "active"
            }
        except:
            return {
                "has_contract_data": True,
                "contract_end_date": contract_end,
                "error": "Could not parse contract end date"
            }
