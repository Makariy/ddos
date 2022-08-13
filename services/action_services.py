from typing import Union, Dict, Tuple, List, Literal
from pydantic import ValidationError

from models import Action

from lib.utils import get_app


ValidationErrorTyping = List[
    Dict[Union[Literal['field', 'msg']], str | int]
]


async def get_action() -> Union[Action, None]:
    app = get_app()
    if hasattr(app.ctx, "action"):
        if app.ctx.action:
            return app.ctx.action

    return None


async def create_action(raw_action: Dict) -> Union[Tuple[Action, None], Tuple[None, ValidationErrorTyping]]:
    try:
        action = Action(**raw_action)
        return action, None
    except ValidationError as e:
        return None, [{
                'field': error['loc'][0],
                'msg': error['msg']
            } for error in e.errors()]


async def set_action(action):
    app = get_app()
    app.ctx.action = action


async def remove_action():
    app = get_app()
    delattr(app.ctx, 'action')
