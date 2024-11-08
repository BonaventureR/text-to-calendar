"""
Calendar Event Builder Module

This module provides functionality to create calendar events using OpenAI's GPT model.
It handles natural language processing of event queries and converts them into structured event data.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

import pytz
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()


class EventBuilder:
    """
    A class to build calendar events from natural language queries.

    Attributes:
        client: OpenAI client instance
        event_structure: JSON schema for calendar events
        tools: List of tools/functions available for the model
        system_prompt: Instructions for the AI model
    """

    def __init__(self, model: str = "gpt-4o") -> None:
        """Initialize the EventBuilder with OpenAI client and event structure."""
        self.model = model
        self.client = OpenAI()
        self._load_event_structure()
        self.tools = [self.event_structure]
        self._set_system_prompt()

    def _load_event_structure(self) -> None:
        """Load the event structure JSON schema from file."""
        current_dir = Path(__file__).resolve().parent
        event_structure_path = current_dir / 'function_call.json'
        with open(event_structure_path, 'r', encoding='utf-8') as file:
            self.event_structure = json.load(file)

    def _set_system_prompt(self) -> None:
        """Set the system prompt for the AI model."""
        self.system_prompt = """
        You are a helpful assistant that helps users create calendar events.
        If the user does not provide extra specific information about anything provided simply create the JSON structure.
        Here is an example of how dateTime should be structured (always in PST):
        {'dateTime': '2015-05-28T09:00:00-07:00', 'timeZone': 'America/Los_Angeles'}
        """

    def _get_current_pacific_time(self) -> str:
        """Get the current time in Pacific timezone with formatted string."""
        pacific_tz = pytz.timezone('America/Los_Angeles')
        curr_time = datetime.now(pacific_tz)
        return curr_time.strftime("%A, %Y-%m-%d %H:%M:%S %Z")

    def build_prompt(self, query: str) -> str:
        """
        Build a prompt for the AI model with the user's query.

        Args:
            query: Natural language query for event creation

        Returns:
            str: Formatted prompt including current time and query
        """
        current_time = self._get_current_pacific_time()
        return f"""
        Below is a query to create a calendar event. The query will be specified within the triple backticks ```query```.
        Here are some default values if the query does not provide them. The current day, date and time is: {current_time}.
        If the query specifies next weekday or weekend, figure out the date and accordingly send the right start and end times.
        If the query does not specify any given time, create a placeholder event in the description by adding [PLACEHOLDER] {{description}} and set it at 9am-10am on the given query day.
        If the query has different time zones, i.e., military time (18:05 or 21:25) convert it to PST before inserting the time.
        If the query does not have a time but two dates, set the {{start.date}} and {{end.date}} properties and do not fill in the dateTime property.
        If the query specifies all the event details, ignore the default values.\n
        Query:```{query}```
        """

    def parse_result(self, response) -> Dict[str, Any]:
        """
        Parse the OpenAI API response into event data.

        Args:
            response: OpenAI API response

        Returns:
            Dict containing parsed event data

        Raises:
            Exception: If parsing fails
        """
        try:
            tool_call = response.choices[0].message.tool_calls[0]
            return json.loads(tool_call.function.arguments)
        except Exception as e:
            raise Exception("Response Parsing error") from e

    def build_event(self, query: str) -> Dict[str, Any]:
        """
        Process a natural language query and return structured event data.

        Args:
            query: Natural language query describing the event

        Returns:
            Dict containing structured event data
        """
        user_prompt = self.build_prompt(query)
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            tools=self.tools
        )
        return self.parse_result(response)
