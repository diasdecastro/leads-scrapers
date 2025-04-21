import logging
from datetime import datetime, timedelta
from typing import List
import time

logger = logging.getLogger(__name__)


class RateLimiter:
    def __init__(self, requests_per_minute: int):
        self.requests_per_minute = requests_per_minute
        self.requests: List[datetime] = []

    def wait(self):
        """Wait if necessary to respect the rate limit."""
        now = datetime.now()
        # Remove requests older than 1 minute
        self.requests = [
            req_time
            for req_time in self.requests
            if now - req_time < timedelta(minutes=1)
        ]

        if len(self.requests) >= self.requests_per_minute:
            # Calculate how long to wait
            oldest_request = self.requests[0]
            wait_time = 60 - (now - oldest_request).total_seconds()
            if wait_time > 0:
                logger.info(f"Rate limit reached. Waiting {wait_time:.2f} seconds...")
                time.sleep(wait_time)

        self.requests.append(now)
