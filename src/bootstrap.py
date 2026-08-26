from clypi import (
    configure,
    ClypiConfig,
    Theme,
    Styler,
    ClypiFormatter,
)

def bootstrap_cli_style():
    """
    Bootstrap the CLI style for the application.
    This function sets up the CLI theme and configuration using ClypiConfig.
    """
    configure(
        ClypiConfig(
            theme=Theme(
                usage=Styler(fg="green", bold=True),
                usage_command=Styler(fg="cyan", bold=True),
                usage_args=Styler(fg="cyan"),
                section_title=Styler(fg="green", bold=True),
                subcommand=Styler(fg="cyan", bold=True),
                long_option=Styler(fg="cyan", bold=True),
                short_option=Styler(fg="cyan", bold=True),
                positional=Styler(fg="cyan"),
                placeholder=Styler(fg="cyan"),
                prompts=Styler(fg="green", bold=True),
            ),
            help_formatter=ClypiFormatter(
                boxed=False,
                show_option_types=False,
            ),
        )
    )