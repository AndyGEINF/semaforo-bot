from pydantic import BaseModel
from typing import List, Optional

class Signal(BaseModel):
    id: int
    type: str
    value: float
    timestamp: str

class Trade(BaseModel):
    id: int
    signal_id: int
    amount: float
    price: float
    timestamp: str

class BotStatus(BaseModel):
    is_running: bool
    current_signal: Optional[Signal]
    trade_history: List[Trade] = []