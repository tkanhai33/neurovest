# Python asyncio cancellation
Source: https://docs.python.org/3.12/library/asyncio-task.html

Task cancellation is delivered by raising asyncio.CancelledError in the task at a cancellation opportunity. Use finally blocks or resource context managers for cleanup. Usually propagate CancelledError after cleanup. Swallowing it can interfere with structured-concurrency features such as TaskGroup and timeout.

