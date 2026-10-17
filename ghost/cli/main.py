"""
GhostOS Command Line Interface (CLI)
Fast, beautiful, offline AI assistant right in your terminal.
"""
import sys
import argparse
from typing import List

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.markdown import Markdown

from ghost.core.engine import GhostEngine
from ghost.core.rag import ZeroDbRAG
from ghost.core.vision import ScreenInspector
from ghost.core.autopilot import TerminalAutopilot
from ghost.core.audio import MeetingCopilot
from ghost.core.memory_juggler import MemoryJuggler

console = Console()

GHOST_ASCII = r"""[bold cyan]
      .---.
     /     \
    | () () |   [bold white]GhostOS[/bold white] [dim]v0.1.0[/dim]
     \  -  /    [dim]The Invisible, Offline Desktop AI[/dim]
    /`---'\
   /       \
  (_/^\_/\_/^)
[/bold cyan]"""

def cmd_ask(engine: GhostEngine, rag: ZeroDbRAG, query: str) -> None:
    """Ask a question with automatic RAG augmentation."""
    # Check if there are relevant local docs
    docs = rag.search(query, top_k=2)
    rag_context = ""
    if docs:
        rag_context = "\n\n".join([f"[{d['filename']}]: {d['content']}" for d in docs])

    console.print(f"[bold dim]Thinking (VRAM Juggler active)...[/bold dim]")
    response = engine.ask(query, context=rag_context)
    console.print(Panel(Markdown(response), title="[bold cyan]👻 Ghost[/bold cyan]", border_style="cyan"))

def cmd_chat(engine: GhostEngine, rag: ZeroDbRAG) -> None:
    """Interactive chat loop."""
    console.print(GHOST_ASCII)
    console.print("[dim]Type your message, or '/exit' to quit, '/screen' to peek, '/status' for VRAM.[/dim]\n")

    while True:
        try:
            user_input = console.input("[bold white]you > [/bold white]").strip()
            if not user_input:
                continue
            if user_input.lower() in {"/exit", "exit", "quit"}:
                console.print("[cyan]Ghost slipped back into the shadows. Goodbye![/cyan]")
                break
            if user_input == "/screen":
                cmd_screen()
                continue
            if user_input == "/status":
                cmd_status()
                continue

            cmd_ask(engine, rag, user_input)
        except (KeyboardInterrupt, EOFError):
            console.print("\n[cyan]Session ended.[/cyan]")
            break

def cmd_eat(rag: ZeroDbRAG, path_str: str) -> None:
    """Ingest a file or directory into Zero-DB RAG."""
    import os
    if os.path.isdir(path_str):
        with console.status(f"[bold cyan]Ghost is consuming directory: {path_str}...[/bold cyan]"):
            res = rag.ingest_directory(path_str)
        if res.get("success"):
            console.print(f"[bold green]✔ Chomp![/bold green] Ingested {res['total_ingested']} files into local knowledge base.")
        else:
            console.print(f"[bold red]✘ Error:[/bold red] {res.get('error')}")
    else:
        with console.status(f"[bold cyan]Ghost is eating {path_str}...[/bold cyan]"):
            res = rag.ingest_file(path_str)
        if res.get("success"):
            console.print(f"[bold green]✔[/bold green] {res['message']} ([dim]{res['size_kb']} KB, {res['chunks_count']} chunks[/dim])")
        else:
            console.print(f"[bold red]✘ Failed to ingest:[/bold red] {res.get('error')}")

def cmd_rag_search(rag: ZeroDbRAG, query: str) -> None:
    """Search the Zero-DB knowledge base."""
    results = rag.search(query, top_k=5)
    if not results:
        console.print("[yellow]No matching documents found in knowledge base.[/yellow]")
        return

    table = Table(title=f"🔎 Search Results for: '{query}'", border_style="cyan")
    table.add_column("File", style="cyan", no_wrap=True)
    table.add_column("Snippet", style="white")
    table.add_column("Rank (BM25)", style="dim", justify="right")

    for r in results:
        snippet = r["content"][:140].replace("\n", " ") + "..."
        table.add_row(r["filename"], snippet, f"{r['rank']:.2f}")

    console.print(table)

def cmd_rag_list(rag: ZeroDbRAG) -> None:
    """List all ingested documents."""
    docs = rag.list_documents()
    if not docs:
        console.print("[dim]Knowledge base is currently empty. Use 'ghost eat <file>' to add documents.[/dim]")
        return

    table = Table(title="📚 Ingested Knowledge Base Documents", border_style="cyan")
    table.add_column("ID", justify="right", style="dim")
    table.add_column("Filename", style="bold cyan")
    table.add_column("Type", style="dim")
    table.add_column("Chunks", justify="right")
    table.add_column("Size", justify="right")
    table.add_column("Ingested At", style="dim")

    for d in docs:
        size_kb = f"{d['size_bytes'] / 1024:.1f} KB" if d['size_bytes'] else "0 KB"
        table.add_row(str(d["id"]), d["filename"], d["file_type"], str(d["chunk_count"]), size_kb, str(d["ingested_at"])[:16])

    console.print(table)

def cmd_screen() -> None:
    """Screen peek and analysis."""
    inspector = ScreenInspector()
    with console.status("[bold cyan]Capturing and analyzing screen...[/bold cyan]"):
        res = inspector.analyze_screen()
    if res.get("success"):
        console.print(Panel(Markdown(res["analysis"]), title="[bold magenta]👁️ Screen Inspector[/bold magenta]", border_style="magenta"))
    else:
        console.print(f"[bold red]✘ Screen capture error:[/bold red] {res.get('error')}")

def cmd_exec(task: str) -> None:
    """Terminal autopilot command generator and runner."""
    pilot = TerminalAutopilot()
    res = pilot.generate_command(task)
    
    cmd = res["command"]
    risk = res["risk"]
    
    console.print(Panel(
        f"[bold white]Task:[/bold white] {task}\n"
        f"[bold white]Suggested Command:[/bold white] [bold yellow]{cmd}[/bold yellow]\n\n"
        f"[dim]{res['explanation']}[/dim]\n\n"
        f"Safety Level: {risk['badge']}" + (f"\n[red]Warning: {risk['warning']}[/red]" if risk['warning'] else ""),
        title="[bold yellow]⚡ Terminal Autopilot[/bold yellow]",
        border_style="yellow"
    ))

    confirm = console.input("[bold cyan]Execute this command now? [y/N]: [/bold cyan]").strip().lower()
    if confirm in {"y", "yes"}:
        console.print("[dim]Executing...[/dim]")
        exec_res = pilot.execute_command(cmd)
        if exec_res["stdout"]:
            console.print(Panel(exec_res["stdout"], title="[green]Output (stdout)[/green]", border_style="green"))
        if exec_res["stderr"]:
            console.print(Panel(exec_res["stderr"], title="[red]Errors (stderr)[/red]", border_style="red"))
        console.print(f"[dim]Process exited with code {exec_res['exit_code']}[/dim]")
    else:
        console.print("[dim]Execution cancelled.[/dim]")

def cmd_status() -> None:
    """Display real-time memory and VRAM juggler status."""
    juggler = MemoryJuggler()
    status = juggler.get_memory_status()

    table = Table(title="🧠 GhostOS VRAM Juggler Status", border_style="cyan")
    table.add_column("Metric", style="bold cyan")
    table.add_column("Value", style="bold white")

    table.add_row("Active Model State", f"[green]{status['active_model']}[/green]")
    table.add_row("Active VRAM Allocation", f"{status['active_vram_mb']} MB")
    table.add_row("VRAM Saved by Swapping", f"[bold green]+{status['vram_saved_mb']} MB[/bold green] (vs concurrent load)")
    table.add_row("Total Model Swaps", str(status["total_swaps"]))
    table.add_row("System RAM Usage", f"{status['system_ram_percent']}% ({status['system_ram_used_mb']} MB / {status['system_ram_total_mb']} MB)")
    table.add_row("Idle Watchdog", f"{status['idle_seconds']}s since last call (auto-sleep at 180s)")

    console.print(table)

def cmd_pet() -> None:
    """Launch Desktop Ghost Pet & HUD GUI."""
    try:
        from ghost.ui.app import launch_desktop_pet
        launch_desktop_pet()
    except Exception as e:
        console.print(f"[bold red]Failed to launch Desktop Pet UI:[/bold red] {e}")

def main() -> None:
    KNOWN_COMMANDS = {"ask", "chat", "pet", "eat", "rag", "screen", "exec", "status", "-h", "--help"}
    if len(sys.argv) > 1 and sys.argv[1] not in KNOWN_COMMANDS and not sys.argv[1].startswith("-"):
        sys.argv.insert(1, "ask")

    parser = argparse.ArgumentParser(
        prog="ghost",
        description="GhostOS: Featherweight, Offline AI Assistant & Desktop Companion"
    )
    subparsers = parser.add_subparsers(dest="subcommand", help="Available commands")

    # Ask (one-shot)
    subparsers.add_parser("ask", help="Ask Ghost a question").add_argument("query", nargs="+", help="Question text")
    
    # Interactive chat
    subparsers.add_parser("chat", help="Start interactive terminal chat session")

    # Pet GUI
    subparsers.add_parser("pet", help="Launch floating Ghost Desktop Pet & Quick HUD")

    # Eat / Ingest
    eat_parser = subparsers.add_parser("eat", help="Feed a file or directory to Ghost (Zero-DB RAG)")
    eat_parser.add_argument("path", help="Path to file or folder to ingest")

    # RAG subcommands
    rag_parser = subparsers.add_parser("rag", help="Knowledge base management")
    rag_subs = rag_parser.add_subparsers(dest="rag_cmd")
    rag_search = rag_subs.add_parser("search", help="Search knowledge base")
    rag_search.add_argument("query", nargs="+", help="Search query")
    rag_subs.add_parser("list", help="List all ingested documents")
    rag_subs.add_parser("clear", help="Clear all documents from knowledge base")

    # Screen peek
    subparsers.add_parser("screen", help="Inspect frontmost active screen")

    # Terminal autopilot
    exec_parser = subparsers.add_parser("exec", help="Generate and run terminal commands safely")
    exec_parser.add_argument("task", nargs="+", help="Description of task to perform")

    # Status
    subparsers.add_parser("status", help="Show VRAM Juggler memory diagnostics")

    args, unknown = parser.parse_known_args()

    engine = GhostEngine()
    rag = ZeroDbRAG()

    if not args.subcommand:
        if unknown:
            # Convenience: `ghost "explain this"` -> treated as ask
            cmd_ask(engine, rag, " ".join(unknown))
        else:
            cmd_chat(engine, rag)
        return

    if args.subcommand == "ask":
        cmd_ask(engine, rag, " ".join(args.query))
    elif args.subcommand == "chat":
        cmd_chat(engine, rag)
    elif args.subcommand == "pet":
        cmd_pet()
    elif args.subcommand == "eat":
        cmd_eat(rag, args.path)
    elif args.subcommand == "rag":
        if args.rag_cmd == "search":
            cmd_rag_search(rag, " ".join(args.query))
        elif args.rag_cmd == "list":
            cmd_rag_list(rag)
        elif args.rag_cmd == "clear":
            rag.clear()
            console.print("[green]Knowledge base cleared successfully.[/green]")
        else:
            cmd_rag_list(rag)
    elif args.subcommand == "screen":
        cmd_screen()
    elif args.subcommand == "exec":
        cmd_exec(" ".join(args.task))
    elif args.subcommand == "status":
        cmd_status()

if __name__ == "__main__":
    main()
