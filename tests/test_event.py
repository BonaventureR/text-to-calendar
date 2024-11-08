import unittest
from unittest.mock import patch, MagicMock
from src.event import EventBuilder


class TestEventBuilder(unittest.TestCase):
    def setUp(self):
        self.event_builder = EventBuilder()

    @patch('openai.ChatCompletion.create')
    def test_build_event_success(self, mock_openai):
        # Setup mock response from OpenAI
        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(
                message={
                    'content': '''{
                        "summary": "Vacation Planning with Chris",
                        "description": "Meeting to discuss vacation plans",
                        "start": {
                            "dateTime": "2024-11-21T10:00:00",
                            "timeZone": "America/Los_Angeles"
                        },
                        "end": {
                            "dateTime": "2024-11-21T11:00:00",
                            "timeZone": "America/Los_Angeles"
                        },
                        "attendees": [
                            {"email": "chris@example.com"}
                        ]
                    }'''
                }
            )
        ]
        mock_openai.return_value = mock_response

        # Test input
        query = "set up a meeting about vacation with chris on Nov 21"

        # Execute
        event = self.event_builder.build_event(query)

        # Assert
        self.assertEqual(event['summary'], "Vacation Planning with Chris")
        self.assertEqual(
            event['description'],
            "Meeting to discuss vacation plans")
        self.assertEqual(event['start']['dateTime'], "2024-11-21T10:00:00")
        self.assertEqual(event['end']['dateTime'], "2024-11-21T11:00:00")
        self.assertEqual(event['attendees'][0]['email'], "chris@example.com")

        # Verify OpenAI was called correctly
        mock_openai.assert_called_once()
        call_args = mock_openai.call_args[1]
        self.assertEqual(call_args['model'], self.event_builder.model)
        self.assertIn(query, str(call_args['messages']))

    @patch('openai.ChatCompletion.create')
    def test_build_event_invalid_json(self, mock_openai):
        # Setup mock response with invalid JSON
        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(message={'content': 'Invalid JSON response'})
        ]
        mock_openai.return_value = mock_response

        # Test
        with self.assertRaises(ValueError):
            self.event_builder.build_event("schedule a meeting")

    @patch('openai.ChatCompletion.create')
    def test_build_event_missing_required_fields(self, mock_openai):
        # Setup mock response with missing required fields
        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(
                message={
                    'content': '''{
                        "summary": "Vacation Planning"
                    }'''
                }
            )
        ]
        mock_openai.return_value = mock_response

        # Test
        with self.assertRaises(ValueError):
            self.event_builder.build_event("schedule a meeting")


if __name__ == '__main__':
    unittest.main()
