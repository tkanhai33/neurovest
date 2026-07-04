from pydantic import BaseModel

class NotificationService:
    async def send_notification(self, message: str) -> dict:
        # Simulate notification sending
        return {"message": f"Notification sent: {message}"}
