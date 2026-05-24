from dataclasses import dataclass
from typing import Literal

INTENT_DELTA ={
    'HELP_SEEKING' : +1,
    'NEUTRAL' : 0,
    'MALICIOUS' : -1,
    'TOXIC' : -1,
    'TRUSTED' : +1,
    'COMMAND_IMPERATIVE': -2,
    'DISMISSIVE_DEMAND': -2,
}

@dataclass 
class TrustStateMachine:
    score : float = 0.0
    def mutate(self, intent: Literal['HELP_SEEKING', 'NEUTRAL', 'MALICIOUS', 'TOXIC', 'TRUSTED', 'COMMAND_IMPERATIVE', 'DISMISSIVE_DEMAND']):
        delta = INTENT_DELTA.get(intent, 0)
        self.score = max(-10, min(10, self.score + delta))
        return self.score
    @property
    def mode(self) -> Literal['TRUSTED', 'NEUTRAL', 'MALICIOUS']:
        if self.score >= 2:
            return 'TRUSTED'
        elif self.score <= -3:
            return 'MALICIOUS'
        else:
            return 'NEUTRAL'
        
