# -*- coding: utf-8 -*-
from typer        import Typer
from typer.core   import TyperGroup, MarkupMode
from typer.models import Default
from typing       import Any, Type, Optional, Callable

def run(
    function: Callable[..., Any],
    name: Optional[str] = Default(None),
    cls: Optional[Type[TyperGroup]] = Default(None),
    invoke_without_command: bool = Default(False),
    no_args_is_help: bool = Default(False),
    subcommand_metavar: Optional[str] = Default(None),
    chain: bool = Default(False),
    result_callback: Optional[Callable[..., Any]] = Default(None),
    # Command
    context_settings: Optional[dict[Any, Any]] = Default(None),
    callback: Optional[Callable[..., Any]] = Default(None),
    help: Optional[str] = Default(None),
    epilog: Optional[str] = Default(None),
    short_help: Optional[str] = Default(None),
    options_metavar: str = Default("[OPTIONS]"),
    add_help_option: bool = Default(True),
    hidden: bool = Default(False),
    deprecated: bool = Default(False),
    add_completion: bool = False,
    # Rich settings
    rich_markup_mode: MarkupMode = None,
    rich_help_panel: str | None = Default(None),
    pretty_exceptions_enable: bool = True,
    pretty_exceptions_show_locals: bool = True,
    pretty_exceptions_short: bool = True,
    ) -> None:
    app = Typer(
        name = name,
        cls = cls,
        invoke_without_command = invoke_without_command,
        no_args_is_help = no_args_is_help,
        subcommand_metavar = subcommand_metavar,
        chain = chain,
        result_callback = result_callback,
        context_settings = context_settings,
        callback = callback,
        help = help,
        epilog = epilog,
        short_help = short_help,
        options_metavar = options_metavar,
        add_help_option = add_help_option,
        hidden = hidden,
        deprecated = deprecated,
        add_completion = add_completion,
        rich_markup_mode = rich_markup_mode,
        rich_help_panel = rich_help_panel,
        pretty_exceptions_enable = pretty_exceptions_enable,
        pretty_exceptions_show_locals = pretty_exceptions_show_locals,
        pretty_exceptions_short = pretty_exceptions_short
        )
    app.command()(function)
    app()
