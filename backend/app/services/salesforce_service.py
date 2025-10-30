"""Salesforce CRM API integration service.

Provides interface to Salesforce REST API for enriching client data with CRM information
including account health, revenue, contacts, opportunities, and more.
"""

import httpx
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from uuid import UUID

from app.models.client import Client

logger = logging.getLogger(__name__)


class SalesforceService:
    """Integration with Salesforce CRM API."""

    DEFAULT_API_VERSION = "v58.0"
    REQUEST_TIMEOUT = 30
    TOKEN_URL = "https://login.salesforce.com/services/oauth2/token"

    @staticmethod
    async def authenticate(
        client_id: str,
        client_secret: str,
        username: Optional[str] = None,
        password: Optional[str] = None,
        refresh_token: Optional[str] = None,
        instance_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Authenticate with Salesforce using OAuth 2.0.

        Supports two authentication methods:
        1. Username/Password flow (for testing)
        2. Refresh token flow (for production)

        Args:
            client_id: Salesforce connected app client ID
            client_secret: Salesforce connected app client secret
            username: Salesforce username (for password flow)
            password: Salesforce password + security token (for password flow)
            refresh_token: Refresh token (for refresh token flow)
            instance_url: Salesforce instance URL (optional)

        Returns:
            Dict containing access_token, instance_url, and other auth details

        Raises:
            Exception: If authentication fails
        """
        try:
            async with httpx.AsyncClient(timeout=SalesforceService.REQUEST_TIMEOUT) as client:

                # Refresh token flow (preferred for production)
                if refresh_token:
                    data = {
                        "grant_type": "refresh_token",
                        "client_id": client_id,
                        "client_secret": client_secret,
                        "refresh_token": refresh_token
                    }

                # Username/password flow (for testing/development)
                elif username and password:
                    data = {
                        "grant_type": "password",
                        "client_id": client_id,
                        "client_secret": client_secret,
                        "username": username,
                        "password": password  # Should include security token appended
                    }

                else:
                    raise ValueError("Must provide either refresh_token or username+password")

                logger.info("Attempting Salesforce authentication")
                response = await client.post(SalesforceService.TOKEN_URL, data=data)
                response.raise_for_status()

                auth_data = response.json()
                logger.info("Salesforce authentication successful")

                return {
                    "access_token": auth_data["access_token"],
                    "instance_url": auth_data.get("instance_url", instance_url),
                    "token_type": auth_data.get("token_type", "Bearer"),
                    "issued_at": auth_data.get("issued_at"),
                    "signature": auth_data.get("signature")
                }

        except httpx.HTTPStatusError as e:
            logger.error(f"Salesforce authentication failed: {e.response.status_code} - {e.response.text}")
            raise Exception(f"Salesforce authentication failed: {e.response.text}")

        except Exception as e:
            logger.error(f"Salesforce authentication error: {str(e)}")
            raise

    @staticmethod
    async def search_account(
        access_token: str,
        instance_url: str,
        account_name: Optional[str] = None,
        domain: Optional[str] = None,
        api_version: str = None
    ) -> Optional[Dict[str, Any]]:
        """
        Search for a Salesforce account by name or domain.

        Args:
            access_token: Salesforce access token
            instance_url: Salesforce instance URL
            account_name: Account name to search for
            domain: Website domain to search for
            api_version: Salesforce API version (default: v58.0)

        Returns:
            Account data dict if found, None otherwise
        """
        if not api_version:
            api_version = SalesforceService.DEFAULT_API_VERSION

        # Build SOQL query
        where_clauses = []
        if account_name:
            # Use LIKE for partial matching
            escaped_name = account_name.replace("'", "\\'")
            where_clauses.append(f"Name LIKE '%{escaped_name}%'")

        if domain:
            # Clean domain
            clean_domain = domain.replace("http://", "").replace("https://", "").replace("www.", "")
            escaped_domain = clean_domain.replace("'", "\\'")
            where_clauses.append(f"Website LIKE '%{escaped_domain}%'")

        if not where_clauses:
            raise ValueError("Must provide account_name or domain")

        where_clause = " OR ".join(where_clauses)

        # SOQL query for account with key fields
        query = f"""
            SELECT Id, Name, Website, Industry, NumberOfEmployees,
                   AnnualRevenue, Type, BillingCity, BillingState, BillingCountry,
                   Phone, Description, OwnerId, Owner.Name, Owner.Email,
                   CreatedDate, LastModifiedDate
            FROM Account
            WHERE {where_clause}
            ORDER BY LastModifiedDate DESC
            LIMIT 1
        """

        try:
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }

            async with httpx.AsyncClient(timeout=SalesforceService.REQUEST_TIMEOUT) as client:
                url = f"{instance_url}/services/data/{api_version}/query"
                params = {"q": query}

                logger.info(f"Searching Salesforce account: name={account_name}, domain={domain}")
                response = await client.get(url, params=params, headers=headers)
                response.raise_for_status()

                data = response.json()
                records = data.get("records", [])

                if records:
                    logger.info(f"Found Salesforce account: {records[0]['Name']}")
                    return records[0]
                else:
                    logger.info("No Salesforce account found")
                    return None

        except Exception as e:
            logger.error(f"Salesforce account search error: {str(e)}")
            raise

    @staticmethod
    async def get_account_contacts(
        access_token: str,
        instance_url: str,
        account_id: str,
        api_version: str = None
    ) -> List[Dict[str, Any]]:
        """
        Get contacts for a Salesforce account.

        Args:
            access_token: Salesforce access token
            instance_url: Salesforce instance URL
            account_id: Salesforce account ID
            api_version: Salesforce API version

        Returns:
            List of contact dictionaries
        """
        if not api_version:
            api_version = SalesforceService.DEFAULT_API_VERSION

        query = f"""
            SELECT Id, Name, Title, Email, Phone, MobilePhone,
                   Department, IsPrimary__c, CreatedDate, LastModifiedDate
            FROM Contact
            WHERE AccountId = '{account_id}' AND IsDeleted = false
            ORDER BY IsPrimary__c DESC NULLS LAST, CreatedDate ASC
            LIMIT 10
        """

        try:
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }

            async with httpx.AsyncClient(timeout=SalesforceService.REQUEST_TIMEOUT) as client:
                url = f"{instance_url}/services/data/{api_version}/query"
                params = {"q": query}

                response = await client.get(url, params=params, headers=headers)
                response.raise_for_status()

                data = response.json()
                return data.get("records", [])

        except Exception as e:
            logger.error(f"Salesforce contacts fetch error: {str(e)}")
            return []

    @staticmethod
    async def get_account_opportunities(
        access_token: str,
        instance_url: str,
        account_id: str,
        api_version: str = None
    ) -> List[Dict[str, Any]]:
        """
        Get opportunities for a Salesforce account.

        Args:
            access_token: Salesforce access token
            instance_url: Salesforce instance URL
            account_id: Salesforce account ID
            api_version: Salesforce API version

        Returns:
            List of opportunity dictionaries
        """
        if not api_version:
            api_version = SalesforceService.DEFAULT_API_VERSION

        query = f"""
            SELECT Id, Name, StageName, Amount, CloseDate, Probability,
                   Type, LeadSource, IsClosed, IsWon, CreatedDate
            FROM Opportunity
            WHERE AccountId = '{account_id}' AND IsClosed = false
            ORDER BY CloseDate ASC
            LIMIT 10
        """

        try:
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }

            async with httpx.AsyncClient(timeout=SalesforceService.REQUEST_TIMEOUT) as client:
                url = f"{instance_url}/services/data/{api_version}/query"
                params = {"q": query}

                response = await client.get(url, params=params, headers=headers)
                response.raise_for_status()

                data = response.json()
                return data.get("records", [])

        except Exception as e:
            logger.error(f"Salesforce opportunities fetch error: {str(e)}")
            return []

    @staticmethod
    async def get_account_cases(
        access_token: str,
        instance_url: str,
        account_id: str,
        api_version: str = None
    ) -> List[Dict[str, Any]]:
        """
        Get open cases for a Salesforce account.

        Args:
            access_token: Salesforce access token
            instance_url: Salesforce instance URL
            account_id: Salesforce account ID
            api_version: Salesforce API version

        Returns:
            List of case dictionaries
        """
        if not api_version:
            api_version = SalesforceService.DEFAULT_API_VERSION

        query = f"""
            SELECT Id, CaseNumber, Subject, Status, Priority, Origin,
                   Type, CreatedDate, LastModifiedDate
            FROM Case
            WHERE AccountId = '{account_id}' AND IsClosed = false
            ORDER BY CreatedDate DESC
            LIMIT 10
        """

        try:
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }

            async with httpx.AsyncClient(timeout=SalesforceService.REQUEST_TIMEOUT) as client:
                url = f"{instance_url}/services/data/{api_version}/query"
                params = {"q": query}

                response = await client.get(url, params=params, headers=headers)
                response.raise_for_status()

                data = response.json()
                return data.get("records", [])

        except Exception as e:
            logger.error(f"Salesforce cases fetch error: {str(e)}")
            return []

    @staticmethod
    async def get_enriched_account_data(
        access_token: str,
        instance_url: str,
        client: Client,
        api_version: str = None
    ) -> Dict[str, Any]:
        """
        Get comprehensive enriched CRM data for a client from Salesforce.

        Args:
            access_token: Salesforce access token
            instance_url: Salesforce instance URL
            client: Client model instance
            api_version: Salesforce API version

        Returns:
            Dict with standardized CRM enrichment data
        """
        try:
            # Search for account
            account = await SalesforceService.search_account(
                access_token=access_token,
                instance_url=instance_url,
                account_name=client.name,
                domain=client.domain,
                api_version=api_version
            )

            if not account:
                logger.warning(f"No Salesforce account found for client: {client.name}")
                return {
                    "found": False,
                    "message": "Account not found in Salesforce"
                }

            account_id = account["Id"]

            # Fetch related data in parallel
            import asyncio
            contacts, opportunities, cases = await asyncio.gather(
                SalesforceService.get_account_contacts(access_token, instance_url, account_id, api_version),
                SalesforceService.get_account_opportunities(access_token, instance_url, account_id, api_version),
                SalesforceService.get_account_cases(access_token, instance_url, account_id, api_version),
                return_exceptions=True
            )

            # Handle any errors from parallel fetches
            if isinstance(contacts, Exception):
                logger.error(f"Error fetching contacts: {str(contacts)}")
                contacts = []
            if isinstance(opportunities, Exception):
                logger.error(f"Error fetching opportunities: {str(opportunities)}")
                opportunities = []
            if isinstance(cases, Exception):
                logger.error(f"Error fetching cases: {str(cases)}")
                cases = []

            # Normalize contact data
            normalized_contacts = []
            for contact in contacts[:5]:  # Limit to 5 contacts
                normalized_contacts.append({
                    "name": contact.get("Name"),
                    "title": contact.get("Title"),
                    "email": contact.get("Email"),
                    "phone": contact.get("Phone") or contact.get("MobilePhone"),
                    "is_primary": contact.get("IsPrimary__c", False)
                })

            # Build standardized enrichment data
            enrichment = {
                "found": True,
                "account_id": account_id,
                "account_name": account.get("Name"),
                "annual_revenue": account.get("AnnualRevenue"),
                "annual_revenue_formatted": f"${int(account.get('AnnualRevenue', 0)):,}" if account.get("AnnualRevenue") else None,
                "employee_count": account.get("NumberOfEmployees"),
                "industry": account.get("Industry"),
                "account_type": account.get("Type"),
                "location": {
                    "city": account.get("BillingCity"),
                    "state": account.get("BillingState"),
                    "country": account.get("BillingCountry")
                },
                "account_owner": {
                    "name": account.get("Owner", {}).get("Name") if isinstance(account.get("Owner"), dict) else None,
                    "email": account.get("Owner", {}).get("Email") if isinstance(account.get("Owner"), dict) else None
                },
                "contacts": normalized_contacts,
                "open_opportunities": len(opportunities),
                "opportunities": [
                    {
                        "name": opp.get("Name"),
                        "stage": opp.get("StageName"),
                        "amount": opp.get("Amount"),
                        "close_date": opp.get("CloseDate"),
                        "probability": opp.get("Probability")
                    }
                    for opp in opportunities[:5]
                ],
                "open_cases": len(cases),
                "cases": [
                    {
                        "case_number": case.get("CaseNumber"),
                        "subject": case.get("Subject"),
                        "status": case.get("Status"),
                        "priority": case.get("Priority")
                    }
                    for case in cases[:5]
                ],
                "created_date": account.get("CreatedDate"),
                "last_modified_date": account.get("LastModifiedDate"),
                "source": "Salesforce",
                "fetched_at": datetime.utcnow().isoformat()
            }

            logger.info(f"Successfully enriched client {client.name} with Salesforce data")
            return enrichment

        except Exception as e:
            logger.error(f"Failed to enrich client {client.name} with Salesforce data: {str(e)}")
            return {
                "found": False,
                "error": str(e),
                "message": "Failed to fetch Salesforce data"
            }

    @staticmethod
    async def test_connection(
        client_id: str,
        client_secret: str,
        refresh_token: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Test Salesforce API connection.

        Args:
            client_id: Salesforce connected app client ID
            client_secret: Salesforce connected app client secret
            refresh_token: Refresh token (optional)
            username: Salesforce username (optional)
            password: Salesforce password + security token (optional)

        Returns:
            Dict with test results
        """
        try:
            start_time = datetime.utcnow()

            # Attempt authentication
            auth_result = await SalesforceService.authenticate(
                client_id=client_id,
                client_secret=client_secret,
                refresh_token=refresh_token,
                username=username,
                password=password
            )

            response_time = (datetime.utcnow() - start_time).total_seconds() * 1000

            return {
                "success": True,
                "status": "success",
                "message": "Salesforce API connection successful",
                "response_time_ms": round(response_time, 2),
                "instance_url": auth_result.get("instance_url")
            }

        except Exception as e:
            return {
                "success": False,
                "status": "failed",
                "message": f"Salesforce API connection failed: {str(e)}",
                "response_time_ms": None
            }
