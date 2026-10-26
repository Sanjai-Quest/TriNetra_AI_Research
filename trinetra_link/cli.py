from __future__ import annotations

import sys
from pathlib import Path
from typing import Optional
import typer

from trinetra_link import __version__
from trinetra_link.fit import fit_thresholds
from trinetra_link.schema.export import export_schemas
from trinetra_link.store.database import Store

app = typer.Typer(
    name="trinetra",
    help="TriNetra-Link: Deterministic Multimodal Chain-of-Custody Attribution Research CLI",
    add_completion=False,
)


@app.command()
def version() -> None:
    """Print the active TriNetra-Link software version."""
    typer.echo(f"TriNetra-Link v{__version__}")


@app.command("export-schema")
def export_schema_cmd(
    output_dir: Optional[str] = typer.Option(None, "--output", "-o", help="Target output directory for JSON schemas")
) -> None:
    """Export Pydantic models to JSON schema files in docs/schema/."""
    export_schemas(output_dir)
    typer.echo("JSON Schemas successfully exported.")


@app.command("fit")
def fit_cmd(
    split: str = typer.Option("calibration", "--split", "-s", help="Dataset split to fit thresholds on (must be calibration)"),
    db_path: Optional[str] = typer.Option(None, "--db", help="Path to SQLite store"),
) -> None:
    """Fit quality, weight, visual, and Bayesian thresholds on calibration split."""
    if split != "calibration":
        typer.secho(
            f"ERROR: Fitting is strictly permitted only on 'calibration' split (received '{split}').",
            fg=typer.colors.RED,
            err=True,
        )
        raise typer.Exit(code=1)

    store = Store(db_path)
    # Collect calibration journeys from store
    # If store is empty, load fixtures/synthetic calibration fixtures if allowed
    journeys = []  # Will load from store or calibration dataset
    try:
        res = fit_thresholds(journeys, split_name=split)
        typer.secho(f"Successfully fitted thresholds: {res['saved_path']}", fg=typer.colors.GREEN)
        typer.echo(f"  theta (quality)   = {res['theta']:.2f}")
        typer.echo(f"  z (weight)        = {res['z_weight']:.2f}")
        typer.echo(f"  tau (bayes)       = {res['tau_bayes']:.2f}")
        typer.echo(f"  visual_threshold  = {res['visual_threshold']:.2f}")
    except Exception as e:
        typer.secho(f"Fit failed: {e}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=2)


@app.command("serve")
def serve_cmd(
    host: str = typer.Option("0.0.0.0", "--host", "-h", help="Bind host address"),
    port: int = typer.Option(8000, "--port", "-p", help="Port number"),
) -> None:
    """Launch the TriNetra-Link Ingest API and Mobile Capture web server."""
    import uvicorn
    from trinetra_link.ingest.api import app as fastapi_app

    typer.echo(f"Starting TriNetra-Link Ingest API on http://{host}:{port} ...")
    uvicorn.run(fastapi_app, host=host, port=port)


if __name__ == "__main__":
    app()
