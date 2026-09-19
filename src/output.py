import time

from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from checks import CheckResult, CheckStatus

console = Console()


def print_header(target: str) -> None:
    """Print the application header."""
    title = Text()
    title.append("BeforePush", style="bold cyan")
    title.append("\nGit branch readiness check", style="dim")

    console.print()
    console.print(
        Panel(
            title,
            border_style="bright_blue",
            padding=(0, 2),
        )
    )

    console.print(f"  [dim]Target[/dim]     [bold]{target}[/bold]")
    console.print()


def get_check_display(result: CheckResult) -> tuple[str, str]:
    """Return the symbol and style for a check result."""
    if result.status == CheckStatus.PASS:
        return "✓", "green"

    if result.status == CheckStatus.WARNING:
        return "⚠", "yellow"

    return "✗", "red"


def print_check(result: CheckResult, animate: bool = True) -> None:
    """Print a single check result."""
    symbol, style = get_check_display(result)

    if animate and console.is_terminal:
        with console.status(
            f"  [dim]Checking {result.name.lower()}...[/dim]",
            spinner="dots",
        ):
            time.sleep(0.25)

    console.print(f"  [{style}]{symbol}[/{style}]  [bold]{result.name}[/bold]")
    console.print(f"     [dim]{result.message}[/dim]")
    console.print()


def print_summary(
    results: list[CheckResult],
) -> None:
    """Print the final readiness summary."""
    failed = sum(result.status == CheckStatus.FAIL for result in results)

    warnings = sum(result.status == CheckStatus.WARNING for result in results)

    console.print("  [dim]" + "─" * 44 + "[/dim]")
    console.print()

    if failed == 0 and warnings == 0:
        summary = Text()
        summary.append("✓ READY\n", style="bold green")
        summary.append(
            "All checks passed. Safe to push.",
            style="green",
        )

        console.print(
            Panel(
                summary,
                border_style="green",
                padding=(0, 2),
            )
        )

    else:
        parts = []

        if failed:
            word = "check" if failed == 1 else "checks"
            parts.append(f"{failed} {word} failed")

        if warnings:
            word = "warning" if warnings == 1 else "warnings"
            parts.append(f"{warnings} {word}")

        summary = Text()
        summary.append("✗ NOT READY\n", style="bold red")
        summary.append(
            f"{' · '.join(parts)}.",
            style="red",
        )

        console.print(
            Panel(
                summary,
                border_style="red",
                padding=(0, 2),
            )
        )

    console.print()


def print_results(
    results: list[CheckResult],
) -> None:
    """Print all check results and the final status."""
    console.print("  [bold]Checks[/bold]")
    console.print()

    animate = console.is_terminal

    for result in results:
        print_check(result, animate=animate)

    print_summary(results)


def display_results(
    results: list[CheckResult],
    target: str,
) -> None:
    """Display the complete check report."""
    print_header(target)

    if console.is_terminal:
        with console.status(
            "[bold cyan]Running checks...[/bold cyan]",
            spinner="dots",
        ):
            time.sleep(0.5)

    print_results(results)
