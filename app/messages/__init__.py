from dataclasses import dataclass

@dataclass
class MoveRequest:
    transaction_id: int
    fen: str

@dataclass
class MoveResponse:
    transaction_id: int
    move: str
