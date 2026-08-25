from datetime import datetime
from typing import Dict, Any, List
from app.models.business_schema import AgentLog

class BaseAgent:
    def __init__(self, name: str, role: str):
        self.name = name
        self.role = role

    def log(self, action: str, thought: str) -> AgentLog:
        return AgentLog(
            agent=self.name,
            role=self.role,
            action=action,
            thought=thought,
            timestamp=datetime.now().strftime("%H:%M:%S")
        )
