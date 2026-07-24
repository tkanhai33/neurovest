class CognitiveNode:
    def __init__(self, name: str):
        self.name = name
        self.state = "idle"
        self.last_event = None
        self.activity_count = 0

    async def on_event(self, event: dict):
        self.state = "active"
        self.last_event = event
        self.activity_count += 1
