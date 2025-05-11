import json
from render_relay.core.bridge.bridge_ops import BridgeOperation

from typing import Optional, Dict

class SSROperation:
    def __init__(self):
        try:
            self.bridge  = BridgeOperation()
        except Exception as e:
            raise Exception(f"Bridge connection error {e}") 

    def render(self, props:Optional[Dict]={}):
        try:
            return self.bridge.send_and_receive(json.dumps({"type":"ssr","data":props}))
        except Exception as e:
            raise Exception(e) 
        