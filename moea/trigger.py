import pygtrie
import copy
from typing import Dict, Any, Optional, List


class BaseTrigger:
    def add(self, x, sf: "ServiceFunc"):
        raise NotImplementedError

    def find_handler(self, event):
        raise NotImplementedError


class PrefixTrigger(BaseTrigger):
    def __init__(self):
        super().__init__()
        self.trie = pygtrie.CharTrie()

    def add(self, prefix, sf):
        if prefix in self.trie:
            self.trie[prefix].append(sf)
        else:
            self.trie[prefix] = [sf]

    """def find_handler(self, event):
        first_event_msg = event.message[0]
        if first_event_msg['type'] != 'text':
            return
        first_text = first_event_msg['data'].lstrip()
        item = self.trie.longest_prefix(first_text)
        if not item:
            return
        old_message = copy.deepcopy(event.message)
        event["prefix"] = item.key
        first_text = first_text[len(item.key):].lstrip()
        if not first_text and len(event.message) > 1:
            del event.message[0]
        else:
            first_event_msg['data'] = first_text

        for sf in item.value:
            yield print(sf)

        event.message = old_message"""

    def find_handler(self, event):
        
        if event.msg_type != 0:
            return
        
        first_text = event.msg.lstrip()
        item = self.trie.longest_prefix(first_text)
        print(item)
        print(item.key, type(item.key))
        print(f'item.value={item.value}, type={type(item.value)}')
        if not item:
            return
        old_message = copy.deepcopy(event.msg)

        first_text = first_text[len(item.key):].lstrip()
        for sf in item.value:
            if not sf:
                print("the sf is None!!!!!!!")
                return
            yield print(sf)
        


        



class CQEvent(dict):

    message: Optional[Any]
    user_id: Optional[int]

    def __getattr__(self, key) -> Optional[Any]:
        return self.get(key)

    def __setattr__(self, key, value) -> None:
        self[key] = value

    def __repr__(self) -> str:
        return f'<Event, {super().__repr__()}>'


prefix = PrefixTrigger()
# suffix = SuffixTrigger()
# keyword = KeywordTrigger()
# rex = RexTrigger()

chain: List[BaseTrigger] = [
    prefix,
    # suffix,
    # _TextNormalizer(),
    # rex,
    # keyword,
]
