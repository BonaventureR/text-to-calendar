import unittest
from unittest.mock import MagicMock, patch
from google.oauth2.credentials import Credentials
from src.gcal import Calendar, SCOPES, TOKEN_FILE, CREDENTIALS_FILE


class TestCalendar(unittest.TestCase):
    def setUp(self):
        self.calendar = Calendar()

    def test_init(self):
        """Test Calendar initialization"""
        self.assertIsNone(self.calendar.credentials)
        self.assertIsNone(self.calendar.service)

    @patch('os.path.exists')
    @patch('google.oauth2.credentials.Credentials.from_authorized_user_file')
    def test_get_refresh_credentials_existing_valid(
            self, mock_creds, mock_exists):
        """Test credential refresh with existing valid credentials"""
        # Setup
        mock_exists.return_value = True
        mock_credentials = MagicMock(spec=Credentials)
        mock_credentials.valid = True
        mock_creds.return_value = mock_credentials

        # Execute
        self.calendar._get_or_refresh_credentials()

        # Assert
        mock_exists.assert_called_once_with(TOKEN_FILE)
        mock_creds.assert_called_once_with(TOKEN_FILE, SCOPES)
        self.assertEqual(self.calendar.credentials, mock_credentials)

    @patch('os.path.exists')
    @patch('google.oauth2.credentials.Credentials.from_authorized_user_file')
    def test_get_refresh_credentials_existing_expired(
            self, mock_creds, mock_exists):
        """Test credential refresh with existing expired credentials"""
        # Setup
        mock_exists.return_value = True
        mock_credentials = MagicMock(spec=Credentials)
        mock_credentials.valid = False
        mock_credentials.expired = True
        mock_credentials.refresh_token = True
        mock_creds.return_value = mock_credentials

        # Execute
        self.calendar._get_or_refresh_credentials()

        # Assert
        mock_exists.assert_called_once_with(TOKEN_FILE)
        mock_credentials.refresh.assert_called_once()

    @patch('os.path.exists')
    @patch('google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file')
    def test_get_refresh_credentials_new(self, mock_flow, mock_exists):
        """Test credential creation when no existing credentials"""
        # Setup
        mock_exists.return_value = False
        mock_flow_instance = MagicMock()
        mock_flow.return_value = mock_flow_instance
        mock_credentials = MagicMock(spec=Credentials)
        mock_flow_instance.run_local_server.return_value = mock_credentials

        # Execute
        self.calendar._get_or_refresh_credentials()

        # Assert
        mock_exists.assert_called_once_with(TOKEN_FILE)
        mock_flow.assert_called_once_with(CREDENTIALS_FILE, SCOPES)
        mock_flow_instance.run_local_server.assert_called_once_with(port=0)
        self.assertEqual(self.calendar.credentials, mock_credentials)


if __name__ == '__main__':
    unittest.main()
