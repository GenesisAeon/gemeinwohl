"""CLI entry-point for the ``gemeinwohl`` command.

Usage examples::

    gemeinwohl assess --entropy 0.3 --models gpt-4 claude-3-sonnet
    gemeinwohl assess --entropy 0.5 --visualize
    gemeinwohl assess --entropy 0.2 --export result.json
    gemeinwohl policy infer --entropy 0.75
    gemeinwohl kritikalitaet check --entropy 0.6 --models llama-3
"""

from __future__ import annotations

import json
from pathlib import Path  # noqa: TC003
from typing import Annotated

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from gemeinwohl.core.gemeinwohl import GemeinwohlEngine
from gemeinwohl.core.kritikalitaet import KritikalitaetsChecker
from gemeinwohl.governance.policy import PersonhoodLevel, PolicyEngine

app = typer.Typer(
    name="gemeinwohl",
    help=(
        "Normative Common-Good Layer for GenesisAeon.\n\n"
        "Compute Gemeinwohl Scores, assess ethical implications, "
        "and enforce personhood-aligned governance policies."
    ),
    add_completion=True,
    rich_markup_mode="rich",
)

assess_app = typer.Typer(help="Assessment commands.")
policy_app = typer.Typer(help="Policy and personhood commands.")
kritikalitaet_app = typer.Typer(help="Criticality checking commands.")

app.add_typer(assess_app, name="assess")
app.add_typer(policy_app, name="policy")
app.add_typer(kritikalitaet_app, name="kritikalitaet")

console = Console()
err_console = Console(stderr=True)


def _version_callback(value: bool) -> None:
    if value:
        from gemeinwohl import __version__

        typer.echo(f"gemeinwohl {__version__}")
        raise typer.Exit


@app.callback()
def main(
    version: Annotated[
        bool | None,
        typer.Option(
            "--version",
            "-V",
            callback=_version_callback,
            is_eager=True,
            help="Show version and exit.",
        ),
    ] = None,
) -> None:
    """Gemeinwohl - Normative Common-Good Layer for GenesisAeon."""


# ---------------------------------------------------------------------------
# assess sub-commands
# ---------------------------------------------------------------------------


@assess_app.callback(invoke_without_command=True)
def assess(
    ctx: typer.Context,
    entropy: Annotated[
        float,
        typer.Option("--entropy", "-e", help="System entropy in [0, 1]."),
    ],
    models: Annotated[
        list[str] | None,
        typer.Option("--models", "-m", help="Model identifiers to include."),
    ] = None,
    personhood: Annotated[
        int,
        typer.Option("--personhood", "-p", help="Personhood level [0-4].", min=0, max=4),
    ] = 0,
    ecological: Annotated[
        float,
        typer.Option("--ecological", help="Ecological impact score in [0, 1]."),
    ] = 0.7,
    equity: Annotated[
        float,
        typer.Option("--equity", help="Social equity score in [0, 1]."),
    ] = 0.6,
    visualize: Annotated[
        bool,
        typer.Option("--visualize", "-v", help="Display a rich summary table."),
    ] = False,
    export: Annotated[
        Path | None,
        typer.Option("--export", help="Export result as JSON to this file path."),
    ] = None,
    full: Annotated[
        bool,
        typer.Option("--full", help="Include ethical implications and recommendations."),
    ] = False,
) -> None:
    """Compute the Gemeinwohl Score for the given parameters.

    Examples:
        gemeinwohl assess --entropy 0.3 --models gpt-4 claude-3-sonnet --visualize

        gemeinwohl assess --entropy 0.5 --full --export report.json
    """
    if ctx.invoked_subcommand is not None:  # pragma: no cover
        return

    try:
        level = PersonhoodLevel(personhood)
    except ValueError:  # pragma: no cover
        err_console.print(f"[red]Invalid personhood level: {personhood}. Must be 0-4.[/red]")
        raise typer.Exit(code=1) from None

    engine = GemeinwohlEngine()
    checker = KritikalitaetsChecker()
    policy = PolicyEngine(default_personhood=level)

    resolved_models = list(models) if models else []

    score = engine.compute_score(
        entropy=entropy,
        models=resolved_models,
        personhood_level=level.weighting_factor,
        ecological_impact=ecological,
        social_equity=equity,
    )

    report = checker.assess(score)
    alignment = policy.evaluate_alignment("cli-system", score, target_level=level)

    if visualize or full:
        _render_full_report(score, report, alignment, full=full)
    else:
        _render_compact(score)

    if export:
        data = {
            "score": score.to_dict(),
            "report": report.to_dict(),
            "alignment": alignment.to_dict(),
        }
        export.write_text(json.dumps(data, indent=2))
        console.print(f"\n[green]Result exported to {export}[/green]")

    from gemeinwohl.core.kritikalitaet import KritikalitaetsLevel

    if report.level == KritikalitaetsLevel.EMERGENCY:
        raise typer.Exit(code=2)


def _render_compact(score: object) -> None:
    from gemeinwohl.core.gemeinwohl import GemeinwohlScore

    if not isinstance(score, GemeinwohlScore):  # pragma: no cover
        return
    colour = _score_colour(score.value)
    console.print(
        f"\nGemeinwohl Score: [{colour}]{score.value:.4f}[/{colour}]"
        f"  - {score.interpretation}"
    )


def _render_full_report(
    score: object,
    report: object,
    alignment: object,
    full: bool = False,
) -> None:
    from gemeinwohl.core.gemeinwohl import GemeinwohlScore
    from gemeinwohl.core.kritikalitaet import KritikalitaetsReport
    from gemeinwohl.governance.policy import GemeinwohlAlignment

    if not (  # pragma: no cover
        isinstance(score, GemeinwohlScore)
        and isinstance(report, KritikalitaetsReport)
        and isinstance(alignment, GemeinwohlAlignment)
    ):
        return

    colour = _score_colour(score.value)
    panel_title = (
        f"[bold]Gemeinwohl Assessment[/bold]  "
        f"[{colour}]{score.value:.4f}[/{colour}]"
    )
    console.print(Panel(score.interpretation, title=panel_title, expand=False))

    table = Table(title="Normative Sub-Scores", show_header=True, header_style="bold cyan")
    table.add_column("Dimension", style="dim")
    table.add_column("Score", justify="right")
    table.add_column("Bar", justify="left")

    for metric, val in score.sub_scores.items():
        bar = "█" * int(val * 20) + "░" * (20 - int(val * 20))
        c = _score_colour(val)
        table.add_row(
            metric.value.replace("_", " ").title(),
            f"[{c}]{val:.4f}[/{c}]",
            f"[{c}]{bar}[/{c}]",
        )
    console.print(table)

    level_colours = {
        "SAFE": "green",
        "WARNING": "yellow",
        "CRITICAL": "red",
        "EMERGENCY": "bold red",
    }
    lc = level_colours.get(report.level.name, "white")
    console.print(f"\nCriticality Level: [{lc}]{report.level.name}[/{lc}]")

    al_c = "green" if alignment.is_aligned else "red"
    console.print(
        f"Personhood Alignment [{alignment.personhood_level.name}]: "
        f"[{al_c}]{'PASS' if alignment.is_aligned else 'FAIL'}[/{al_c}]"
        f"  (required >= {alignment.required_minimum:.2f},"
        f" gap = {alignment.gap:+.4f})"
    )

    if full and report.implications:
        impl_table = Table(
            title="Ethical Implications",
            show_header=True,
            header_style="bold magenta",
        )
        impl_table.add_column("Code")
        impl_table.add_column("Severity", justify="right")
        impl_table.add_column("Description")
        for imp in report.implications:
            ic = "red" if imp.severity >= 0.7 else ("yellow" if imp.severity >= 0.4 else "green")
            impl_table.add_row(
                imp.code, f"[{ic}]{imp.severity:.2f}[/{ic}]", imp.description
            )
        console.print(impl_table)

    if full and report.recommendations:
        console.print("\n[bold]Governance Recommendations:[/bold]")
        for rec in report.recommendations:
            console.print(f"  * {rec}")


def _score_colour(val: float) -> str:
    if val >= 0.70:
        return "green"
    if val >= 0.50:
        return "yellow"
    if val >= 0.30:
        return "red"
    return "bold red"


# ---------------------------------------------------------------------------
# policy sub-commands
# ---------------------------------------------------------------------------


@policy_app.command("infer")
def policy_infer(
    entropy: Annotated[
        float,
        typer.Option("--entropy", "-e", help="System entropy in [0, 1]."),
    ],
    models: Annotated[
        list[str] | None,
        typer.Option("--models", "-m"),
    ] = None,
    personhood: Annotated[int, typer.Option("--personhood", "-p", min=0, max=4)] = 0,
    ecological: Annotated[float, typer.Option("--ecological")] = 0.7,
    equity: Annotated[float, typer.Option("--equity")] = 0.6,
) -> None:
    """Infer the highest achievable personhood level for given parameters."""
    engine = GemeinwohlEngine()
    policy = PolicyEngine()
    level = PersonhoodLevel(personhood)

    score = engine.compute_score(
        entropy=entropy,
        models=list(models) if models else [],
        personhood_level=level.weighting_factor,
        ecological_impact=ecological,
        social_equity=equity,
    )

    max_level = policy.infer_max_personhood(score)
    console.print(
        f"\nScore: [bold]{score.value:.4f}[/bold]  ->  "
        f"Max Personhood: [green]{max_level.name}[/green] "
        f"(Level {int(max_level)})"
    )
    console.print(f"   {max_level.description}")


@policy_app.command("rules")
def policy_rules() -> None:
    """List all active governance policy rules."""
    policy = PolicyEngine()
    table = Table(title="Active Policy Rules", header_style="bold cyan")
    table.add_column("Rule ID")
    table.add_column("Min Score", justify="right")
    table.add_column("Max Personhood")
    table.add_column("Description")

    for rule in policy.rules:
        table.add_row(
            rule.rule_id,
            f"{rule.min_score:.2f}",
            rule.max_personhood_level.name,
            rule.description,
        )
    console.print(table)


# ---------------------------------------------------------------------------
# kritikalitaet sub-commands
# ---------------------------------------------------------------------------


@kritikalitaet_app.command("check")
def kritikalitaet_check(
    entropy: Annotated[
        float,
        typer.Option("--entropy", "-e", help="System entropy in [0, 1]."),
    ],
    models: Annotated[
        list[str] | None,
        typer.Option("--models", "-m"),
    ] = None,
    personhood: Annotated[int, typer.Option("--personhood", "-p", min=0, max=4)] = 0,
    ecological: Annotated[float, typer.Option("--ecological")] = 0.7,
    equity: Annotated[float, typer.Option("--equity")] = 0.6,
    export: Annotated[
        Path | None,
        typer.Option("--export"),
    ] = None,
) -> None:
    """Run a criticality check and display the full report."""
    engine = GemeinwohlEngine()
    checker = KritikalitaetsChecker()
    level = PersonhoodLevel(personhood)

    score = engine.compute_score(
        entropy=entropy,
        models=list(models) if models else [],
        personhood_level=level.weighting_factor,
        ecological_impact=ecological,
        social_equity=equity,
    )

    report = checker.assess(score)
    level_colours = {
        "SAFE": "green",
        "WARNING": "yellow",
        "CRITICAL": "red",
        "EMERGENCY": "bold red",
    }
    lc = level_colours.get(report.level.name, "white")
    console.print(
        Panel(
            f"Score: [bold]{score.value:.4f}[/bold]\n"
            f"Level: [{lc}]{report.level.name}[/{lc}]",
            title="[bold]Kritikalitaets-Check[/bold]",
            expand=False,
        )
    )

    if report.implications:
        for imp in report.implications:
            ic = "red" if imp.severity >= 0.7 else "yellow"
            console.print(f"  [{ic}][{imp.code}][/{ic}] {imp.description}")

    if report.recommendations:
        console.print("\n[bold]Recommendations:[/bold]")
        for rec in report.recommendations:
            console.print(f"  * {rec}")

    if export:
        export.write_text(json.dumps(report.to_dict(), indent=2))
        console.print(f"\n[green]Report exported to {export}[/green]")

    from gemeinwohl.core.kritikalitaet import KritikalitaetsLevel

    if report.level == KritikalitaetsLevel.EMERGENCY:
        raise typer.Exit(code=2)


if __name__ == "__main__":  # pragma: no cover
    app()
