"""
Google Calendar Integration Module

This module handles the integration with Google Calendar API, including authentication
and event creation functionality.
"""

import os.path
from typing import Dict, Optional, Any

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/calendar"]
TOKEN_FILE = "token.json"
CREDENTIALS_FILE = "credentials.json"


class Calendar:
    """
    A class to handle Google Calendar operations.

    This class manages authentication and provides methods to interact
    with the Google Calendar API.
    """

    def __init__(self) -> None:
        """Initialize the Calendar instance."""
        self.credentials: Optional[Credentials] = None
        self.service = None

    def _get_or_refresh_credentials(self) -> None:
        """
        Get or refresh Google Calendar API credentials.

        Returns:
            Optional[Credentials]: Valid credentials if successful, None otherwise.

        Note:
            This method handles the OAuth2 flow for authentication:
            1. Checks for existing token
            2. Refreshes expired token
            3. Creates new token if none exists
        """
        if os.path.exists(TOKEN_FILE):
            self.credentials = Credentials.from_authorized_user_file(
                TOKEN_FILE, SCOPES)

        if not self.credentials or not self.credentials.valid:
            if self.credentials and self.credentials.expired and self.credentials.refresh_token:
                try:
                    self.credentials.refresh(Request())
                except Exception as e:
                    raise Exception("Error refreshing credentials") from e
            else:
                try:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        CREDENTIALS_FILE, SCOPES
                    )
                    self.credentials = flow.run_local_server(port=0)
                except Exception as e:
                    raise Exception(
                        "Error in gcal credential authentication flow.") from e

            # Save the credentials for future use
            try:
                with open(TOKEN_FILE, "w", encoding='utf-8') as token:
                    token.write(self.credentials.to_json())
            except Exception as e:
                raise Exception("Error saving credentials") from e

    def create_event(self, event: Dict[str, Any]) -> str:
        """
        Create a new event in Google Calendar.

        Args:
            event: Dictionary containing event details following Google Calendar API format.
                  Required fields: summary, start, end
                  Optional fields: description, location, attendees, etc.

        Returns:
            str: HTML link to the created event.

        Raises:
            Exception: If authentication fails or event creation encounters an error.
        """
        try:
            # Ensure we have valid credentials
            self._get_or_refresh_credentials()
            if not self.credentials:
                raise Exception("Failed to obtain valid credentials")

            # Build the Calendar API service
            service = build("calendar", "v3", credentials=self.credentials)

            # Create the event
            created_event = service.events().insert(
                calendarId='primary',
                body=event
            ).execute()

            return created_event.get('htmlLink')

        except HttpError as error:
            raise Exception("Error occurred creating the event.") from error
        except Exception as error:
            raise Exception(
                "Unexpected error while creating the event.") from error
