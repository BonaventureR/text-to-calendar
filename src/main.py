from typing import Optional
from event import EventBuilder
from gcal import Calendar


class EventScheduler:
    def __init__(self, calendar_client=None, event_builder=None):
        self.calendar = calendar_client or Calendar()
        self.event_builder = event_builder or EventBuilder(model="gpt-4o-mini")

    def schedule_meeting(self, query: str) -> Optional[str]:
        """
        Schedule a meeting based on natural language query.

        Args:
            query: Natural language description of the meeting

        Returns:
            str: Calendar event link if successful, None if failed
        """
        try:
            event = self.event_builder.build_event(query)
            link = self.calendar.create_event(event)
            return link
        except Exception as e:
            print(f"Failed to schedule meeting: {str(e)}")
            return None


def main():
    # Example usage
    scheduler = EventScheduler()
    query = "set up a meeting about vacation with chris on Nov 21-Nov 26."

    if link := scheduler.schedule_meeting(query):
        print(f"Meeting scheduled successfully! Link: {link}")
    else:
        print("Failed to schedule meeting")


if __name__ == "__main__":
    main()
