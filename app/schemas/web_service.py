from pydantic import BaseModel, Field
from typing import Dict, Optional, Any

class WebhookPayload(BaseModel):
    event_type: str
    data: Dict[str, Any]
    timestamp: Optional[str] = None

class WebhookResponse(BaseModel):
    status: str
    message: str
    data: Optional[Dict[str, Any]] = None

class CallbackResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None

class NotificationPayload(BaseModel):
    notification_type: str = Field(..., description="Type of notification (email, sms, etc.)")
    recipient: str = Field(..., description="Recipient identifier (email, phone number, etc.)")
    template_id: Optional[str] = None
    data: Dict[str, Any] = Field(default_factory=dict) 