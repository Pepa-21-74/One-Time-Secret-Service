from time import time 
from dataclasses import dataclass

@dataclass 
class AttemptState:
    count_attempt: int = 0
    blocked_until: float = 0.0
    block_attempt_id: int = 0

class Security_Brute_Force:
    def __init__(self):
        self._max_attempts = 5
        self._attempts_state: dict[str, AttemptState] = {}
        self._block_second = 300
    
    def is_blocked(self, client_id: str) -> bool:
        state = self._attempts_state.get(client_id)

        if state == None:
            return False

        if state.blocked_until and state.blocked_until > time():
            return True

        return False

    def unblocking(self, client_id: str) -> bool:
        state = self._attempts_state.get(client_id)

        if state == None:
            return False

        if state.blocked_until and state.blocked_until < time():
            del self._attempts_state[client_id]
            return True

        return False

    def recording_of_failures(self, client_id: str) -> None:
        state = self._attempts_state.setdefault(client_id, AttemptState())
        state.count_attempt += 1

        if state.count_attempt >= self._max_attempts:
            state.blocked_until = time() + self._block_second

        

security_protection = Security_Brute_Force()
