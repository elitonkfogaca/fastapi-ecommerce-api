"""
CLI para gerenciar o projeto.
Uso: python -m app.cli [command]
"""

import asyncio
import typer
from rich.console import Console
from rich.table import Table

from app.database.seed import seed_database, seed_only_admin

app = typer.Typer(help="FastAPI E-commerce API Management CLI")
console = Console()


@app.command()
def seed(
    admin_only: bool = typer.Option(
        False, "--admin-only", help="Create only admin user"
    )
):
    """Populate database with initial data."""

    if admin_only:
        asyncio.run(seed_only_admin())
    else:
        asyncio.run(seed_database())


@app.command()
def info():
    """Show project information and credentials."""

    table = Table(
        title="🚀 FastAPI E-commerce API", show_header=True, header_style="bold cyan"
    )

    table.add_column("Item", style="cyan", width=20)
    table.add_column("Value", style="green")

    table.add_row("API URL", "http://localhost:8000")
    table.add_row("Docs (Swagger)", "http://localhost:8000/docs")
    table.add_row("ReDoc", "http://localhost:8000/redoc")
    table.add_row("Health Check", "http://localhost:8000/health")
    table.add_row("", "")
    table.add_row("Admin Email", "admin@example.com")
    table.add_row("Admin Password", "admin123 ⚠️")
    table.add_row("", "")
    table.add_row("Customer Email", "customer@example.com")
    table.add_row("Customer Password", "customer123")

    console.print(table)
    console.print(
        "\n⚠️  [bold red]CHANGE ADMIN PASSWORD AFTER FIRST LOGIN![/bold red]\n"
    )


if __name__ == "__main__":
    app()
