import inspect
import json
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Type


@dataclass
class StructArg:
    name: str
    arg_type: Type
    allow_default: bool = False
    default_value: Any = None


@dataclass
class StructCommand:
    name: str
    args: List[StructArg]
    return_type: Type


class BaseMcu:
    def __init__(self, name: str, commands: List[StructCommand]) -> None:
        self.name = name
        self.commands = commands
        self._bind_commands()

    def _bind_commands(self) -> None:
        for cmd in self.commands:
            method = self._initial_command_method(cmd)
            setattr(self, cmd.name, method)

    def _initial_command_method(self, cmd: StructCommand) -> Callable[..., Any]:
        def command_func(*args: Any, **kwargs: Any) -> Any:
            bound_args = inspect.signature(command_func).bind(self, *args, **kwargs)
            bound_args.apply_defaults()
            arg_dict: Dict[str, Any] = {}
            for arg in cmd.args:
                arg_value = bound_args.arguments[arg.name]
                arg_dict[arg.name] = arg_value
            print(arg_dict)
            print("arg dict")
            packet = self._encode_command(cmd.name, arg_dict)
            print(f"Sending Command: {cmd.name}")
            print(f"Packed Data: {packet}")
            return self._mock_response(cmd.return_type)

        params = [inspect.Parameter("self", inspect.Parameter.POSITIONAL_OR_KEYWORD)]
        for arg in cmd.args:
            if arg.allow_default:
                param = inspect.Parameter(
                    name=arg.name,
                    kind=inspect.Parameter.POSITIONAL_OR_KEYWORD,
                    default=arg.default_value,
                    annotation=arg.arg_type
                )
            else:
                param = inspect.Parameter(
                    name=arg.name,
                    kind=inspect.Parameter.POSITIONAL_OR_KEYWORD,
                    annotation=arg.arg_type
                )
            params.append(param)

        sig = inspect.Signature(parameters=params, return_annotation=cmd.return_type)
        command_func.__signature__ = sig
        command_func.__name__ = cmd.name

        return command_func

    def _encode_command(self, command_name: str, args: Dict[str, Any]) -> str:
        data = {
            "device": self.name,
            "command": command_name,
            "args": args
        }
        return json.dumps(data)

    def _mock_response(self, return_type: Type) -> Any:
        if return_type == str:
            return "OK"
        elif return_type == int:
            return 42
        elif return_type == float:
            return 3.14
        elif return_type == bool:
            return True
        elif return_type == dict:
            return {"status": "success"}
        else:
            return None


commands = [
    StructCommand(
        name="turn_on_led",
        args=[
            StructArg("color", str),
            StructArg("intensity", int, allow_default=True, default_value=5)
        ],
        return_type=str
    ),
    StructCommand(
        name="move",
        args=[
            StructArg("x", int),
            StructArg("y", int),
            StructArg("speed", float, allow_default=True, default_value=1.0)
        ],
        return_type=dict
    )
]

oriel = BaseMcu("OrielDevice", commands)

print(oriel.turn_on_led("green"))



print(oriel.move(speed=20,y=20,x=10))

