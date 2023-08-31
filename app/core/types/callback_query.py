import json
from functools import cached_property

from pyrogram.types import CallbackQuery as Callback_Query


class CallbackQuery(Callback_Query):
    def __init__(self, query):
        super().__dict__.update(query.__dict__)

    @cached_property
    def cmd(self):
        return self.cbdata.get("cmd")

    @cached_property
    def cbdata(self):
        if not self.data:
            return {}
        try:
            return json.loads(self.data.replace("'", '"'))
        except BaseException:
            return {}

    @classmethod
    def parse_cb(cls, cb):
        return cls(cb)
