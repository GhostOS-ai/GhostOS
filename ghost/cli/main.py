"""
GhostOS Command Line Interface (CLI)
Fast, beautiful, offline AI assistant right in your terminal.
"""
import sys
import argparse
from typing import List, Optional, Dict, Any

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
    """Ask a question with automatic OS agent, live web search, and RAG augmentation."""
    # 1. OS Agent check (find files, open folders, create folders)
    from ghost.core.agent import GhostOSAgent
    agent_res = GhostOSAgent.execute_intent(query)
    if agent_res.get("handled"):
        console.print(Panel(Markdown(agent_res["output"]), title="[bold green]🤖 Ghost Desktop Agent[/bold green]", border_style="green"))
        return

    # 2. Live Web Search check (weather, currency rates)
    q_lower = query.lower()
    if any(w in q_lower for w in ["погода", "weather", "курс", "доллар", "евро", "валют", "найди в интернете"]):
        from ghost.core.web_search import WebSearchEngine
        web_res = WebSearchEngine.search_web(query)
        if web_res.get("content"):
            console.print(Panel(Markdown(web_res["content"]), title=f"[bold cyan]🌐 Web Result ({web_res.get('source', 'Internet')})[/bold cyan]", border_style="cyan"))
            return

    # 3. Check if there are relevant local docs
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
    table.add_row("Idle Watchdog", f"{status['idle_seconds']}s since last call (auto-sleep at {status['effective_sleep_seconds']}s)")
    if "chameleon_profile" in status and status["chameleon_profile"]:
        prof = status["chameleon_profile"]
        table.add_row("Chameleon Power Profile", f"[bold yellow]{prof.get('name')}[/bold yellow]")

    console.print(table)

def cmd_models(engine: GhostEngine) -> None:
    """Display installed local models and hardware acceleration capabilities."""
    catalog = engine.get_model_catalog()

    table = Table(title="🤖 GhostOS Local Models & Hardware Engine", border_style="cyan")
    table.add_column("Property", style="bold cyan")
    table.add_column("Details", style="bold white")

    table.add_row("Active Inference Engine", f"[green]{catalog['active_backend']}[/green]")
    table.add_row("Hardware Acceleration", f"[bold yellow]{catalog['hardware_acceleration']}[/bold yellow]")
    table.add_row("Ollama Endpoint", f"{catalog['ollama_host']} ({'Online' if catalog['ollama_active'] else 'Offline'})")

    if catalog["ollama_models"]:
        models_str = "\n".join([f"• [bold white]{m['name']}[/bold white] ({m['size_gb']} GB)" for m in catalog["ollama_models"]])
        table.add_row("Installed Ollama Models", models_str)
    else:
        table.add_row("Installed Ollama Models", "[dim]None detected (Run 'ollama run llama3.2' to pull a 2GB model)[/dim]")

    if catalog["gguf_models"]:
        gguf_str = "\n".join([f"• [bold white]{m['name']}[/bold white] ({m['size_gb']} GB)" for m in catalog["gguf_models"]])
        table.add_row("Local GGUF Models", gguf_str)

    console.print(table)

    rec_table = Table(title="💡 Recommended Low-Spec Models", border_style="dim")
    rec_table.add_column("Model", style="bold cyan")
    rec_table.add_column("RAM Footprint", style="green")
    rec_table.add_column("Target Hardware", style="white")

    for r in catalog["recommended_models"]:
        rec_table.add_row(r["name"], r["ram"], r["tier"])

    console.print(rec_table)

def cmd_pet(skin: str = "glass") -> None:
    """Launch Desktop Ghost Pet & HUD GUI."""
    try:
        from ghost.ui.app import launch_desktop_pet
        console.print(f"[bold cyan]👻 Casper ({skin} skin) is floating onto your screen...[/bold cyan]")
        launch_desktop_pet(skin=skin)
    except Exception as e:
        console.print(f"[bold red]Failed to launch Desktop Pet UI:[/bold red] {e}")
        console.print("[dim]Falling back to interactive terminal chat...[/dim]")
        engine = GhostEngine()
        rag = ZeroDbRAG()
        cmd_chat(engine, rag)

def cmd_clip() -> None:
    """Inspect clipboard and execute 1-click contextual action."""
    from ghost.core.clipboard import PhantomClipboard
    res = PhantomClipboard.inspect()
    if not res["detected"]:
        console.print("[dim]Clipboard is empty or contains non-text content.[/dim]")
        return

    table = Table(title="📋 Phantom Clipboard Analysis", border_style="cyan")
    table.add_column("Property", style="bold cyan")
    table.add_column("Value", style="bold white")
    table.add_row("Type", res["badge"])
    table.add_row("Preview", res["preview"])
    table.add_row("Suggested Action", res.get("action_title", "Process snippet"))
    console.print(table)

    if res.get("category") == "error":
        engine = GhostEngine()
        with console.status("[bold cyan]Analyzing error traceback with Context Vacuum...[/bold cyan]"):
            fix = engine.ask(f"Explain this error and give the exact fix:\n\n{res['raw_text']}")
        console.print(Panel(Markdown(fix), title="[bold green]💡 Recommended Fix[/bold green]", border_style="green"))

    elif res.get("category") == "json":
        console.print(Panel(res.get("formatted_text", ""), title="[bold cyan]✨ Validated & Formatted JSON[/bold cyan]", border_style="cyan"))

def cmd_timemachine() -> None:
    """Session journal and git summary."""
    from ghost.core.time_machine import GhostTimeMachine
    res = GhostTimeMachine.generate_session_summary()
    console.print(Panel(Markdown(res["summary"]), title="[bold cyan]🕒 Ghost Time Machine[/bold cyan]", border_style="cyan"))
    if res.get("commit_suggestion"):
        console.print(Panel(f"[bold green]{res['commit_suggestion']}[/bold green]", title="[bold yellow]💡 Recommended Git Commit[/bold yellow]", border_style="yellow"))

def cmd_rpg() -> None:
    """Display Casper RPG level, XP, and unlocked evolution accessories."""
    from ghost.core.rpg import CasperRPG
    stats = CasperRPG.get_full_status()

    table = Table(title="🎮 Casper RPG & Evolution Status", border_style="magenta")
    table.add_column("Attribute", style="bold magenta")
    table.add_column("Value", style="bold white")

    table.add_row("Evolution Rank", f"[bold yellow]{stats['badge']}[/bold yellow] ({stats['title']})")
    table.add_row("Current Level", f"Level {stats['level']}")
    table.add_row("Total Experience", f"{stats['xp']} XP")
    table.add_row("Level Progress", f"{stats['progress_percent']}% to next evolution")
    table.add_row("Active Accessory", f"[cyan]{stats['accessory']}[/cyan]")
    table.add_row("Files Ingested (Eaten)", str(stats["files_eaten"]))
    table.add_row("Tasks / Questions", str(stats["questions_answered"]))

    console.print(table)

def cmd_chameleon() -> None:
    """Display adaptive power and memory profile."""
    from ghost.core.chameleon import MemoryChameleon
    prof = MemoryChameleon.get_profile()

    table = Table(title="🦎 GhostOS Memory Chameleon", border_style="green")
    table.add_column("Parameter", style="bold green")
    table.add_column("Setting", style="bold white")

    table.add_row("Active Mode", f"[bold green]{prof['name']}[/bold green]")
    table.add_row("Power Source", "🔋 Battery (Eco Throttling)" if prof["is_battery"] else "⚡ Plugged In (Full Metal GPU)")
    table.add_row("System RAM Pressure", f"{prof['ram_pressure_percent']}%")
    table.add_row("Context Window Limit", f"{prof['context_window']} tokens (KV Cache Protected)")
    table.add_row("Active CPU Threads", str(prof["cpu_threads"]))
    table.add_row("Auto-Sleep Timeout", f"{prof['auto_sleep_seconds']}s")

    console.print(table)

def cmd_web(query: str) -> None:
    """Live web search."""
    from ghost.core.web_search import WebSearchEngine
    with console.status(f"[bold cyan]Searching web for: {query}...[/bold cyan]"):
        res = WebSearchEngine.search_web(query)
    console.print(Panel(Markdown(res["content"]), title=f"[bold cyan]🌐 Web Result ({res.get('source', 'Internet')})[/bold cyan]", border_style="cyan"))

def cmd_agent(task: str) -> None:
    """Desktop OS task execution."""
    from ghost.core.agent import GhostOSAgent
    with console.status(f"[bold cyan]Executing OS task: {task}...[/bold cyan]"):
        res = GhostOSAgent.execute_intent(task)
    if res.get("handled"):
        console.print(Panel(Markdown(res["output"]), title="[bold green]🤖 Ghost Desktop Agent[/bold green]", border_style="green"))
    else:
        console.print(f"[yellow]Could not determine automatic OS action for: {task}[/yellow]")

def cmd_say(text: str) -> None:
    """Speak text aloud using native speech synthesis."""
    from ghost.core.voice import VoiceEngine
    voice = VoiceEngine()
    console.print(f"[bold cyan]🗣️ Speaking:[/bold cyan] {text}")
    voice.speak(text, async_mode=False)

def cmd_write(mode: str = "polish", text: Optional[str] = None) -> None:
    """Ghostwriter: Inline text rewrite & transformation via clipboard or text."""
    from ghost.core.ghostwriter import Ghostwriter
    writer = Ghostwriter()
    if text:
        res = writer.rewrite_text(text, mode=mode)
        if res.get("success"):
            console.print(Panel(res["result"], title=f"[bold cyan]✍️ Ghostwriter ({res['title']})[/bold cyan]", border_style="cyan"))
        else:
            console.print(f"[red]Error: {res.get('error')}[/red]")
    else:
        res = writer.rewrite_clipboard(mode=mode)
        if res.get("success"):
            console.print(f"[bold green]✔ Rewritten and copied to clipboard![/bold green] ([dim]{res['title']}[/dim])")
            console.print(Panel(res["result"], title="[bold cyan]📋 Clipboard Content[/bold cyan]", border_style="cyan"))
        else:
            console.print(f"[red]Error: {res.get('error')}[/red]")

def cmd_vault(action: str = "list", key: Optional[str] = None, value: Optional[str] = None) -> None:
    """Memory Vault: Cross-session personal context and facts."""
    from ghost.core.memory_vault import MemoryVault
    vault = MemoryVault()
    if action == "remember" and key and value:
        vault.remember(key, value)
        console.print(f"[bold green]✔ Learned:[/bold green] [cyan]{key}[/cyan] = {value}")
    elif action == "forget" and key:
        success = vault.forget(key)
        if success:
            console.print(f"[yellow]✔ Forgotten:[/yellow] {key}")
        else:
            console.print(f"[dim]Fact '{key}' was not found in vault.[/dim]")
    else:
        facts = vault.get_all_facts()
        if not facts:
            console.print("[dim]Memory Vault is currently empty. Teach Casper with 'ghost vault remember <key> <value>'.[/dim]")
            return
        table = Table(title="🧠 GhostOS Memory Vault (Long-Term Facts)", border_style="cyan")
        table.add_column("Category", style="cyan")
        table.add_column("Key", style="bold white")
        table.add_column("Value", style="green")
        for f in facts:
            table.add_row(f["category"], f["fact_key"], f["fact_value"])
        console.print(table)

def cmd_standup() -> None:
    """Daily Standup & Commit Crafter."""
    from ghost.core.time_machine import GhostTimeMachine
    standup = GhostTimeMachine.generate_daily_standup()
    console.print(Panel(Markdown(standup), title="[bold cyan]📅 Daily Standup Report[/bold cyan]", border_style="cyan"))

def cmd_sandbox(command: str) -> None:
    """Terminal Sandbox Lens: Deep safety analysis."""
    from ghost.core.lens import GhostLens
    res = GhostLens.verify_and_patch(command)
    box = res.get("sandbox", {})
    safety = box.get("safety_level", "SAFE")

    color = "green" if safety == "SAFE" else ("yellow" if safety == "CAUTION" else "red")
    badge = f"[{color} bold]{safety}[/{color} bold]"

    console.print(f"\nCommand: [white bold]{command}[/white bold]")
    console.print(f"Safety Level: {badge}")

    if box.get("is_blocked"):
        console.print(f"[red bold]⛔ BLOCKED BY SANDBOX:[/red bold] {box.get('danger_reason')}")
        if box.get("safe_alternative"):
            console.print(f"[green]Safe alternative:[/green] {box.get('safe_alternative')}")
    elif box.get("danger_reason"):
        console.print(f"[yellow]Warning:[/yellow] {box.get('danger_reason')}")
        if box.get("safe_alternative"):
            console.print(f"[green]Safe alternative:[/green] {box.get('safe_alternative')}")
    else:
        console.print("[green]✔ Command passed all anti-hallucination and destructive checks.[/green]")

def main() -> None:
    KNOWN_COMMANDS = {
        "ask", "chat", "pet", "models", "eat", "rag", "screen", "exec", "status",
        "clip", "clipboard", "time", "timemachine", "rpg", "chameleon",
        "web", "agent", "say", "write", "vault", "standup", "sandbox",
        "-h", "--help"
    }
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
    pet_parser = subparsers.add_parser("pet", help="Launch floating Ghost Desktop Pet & Quick HUD")
    pet_parser.add_argument("--skin", default="glass", choices=["glass", "cyberpunk", "gold", "matrix"], help="Visual skin for Casper (glass, cyberpunk, gold, matrix)")

    # Models / Hardware catalog
    subparsers.add_parser("models", help="Inspect local AI models, Ollama instances, and hardware acceleration")

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

    # New Killer Features CLI commands
    subparsers.add_parser("clip", help="Phantom Clipboard: Inspect & execute 1-click action")
    subparsers.add_parser("clipboard", help="Alias for clip")
    subparsers.add_parser("time", help="Ghost Time Machine: session activity & git commit generator")
    subparsers.add_parser("timemachine", help="Alias for time")
    subparsers.add_parser("rpg", help="Casper RPG: view level, experience, and unlocked evolutions")
    subparsers.add_parser("chameleon", help="Memory Chameleon: view adaptive power & memory profile")
    
    # Voice, Agent, Web Search
    web_parser = subparsers.add_parser("web", help="Live web search (weather, currency, Wikipedia, etc.)")
    web_parser.add_argument("query", nargs="+", help="Search query")

    agent_parser = subparsers.add_parser("agent", help="Desktop OS tasks (find files via Spotlight, create folders)")
    agent_parser.add_argument("task", nargs="+", help="Task description")

    say_parser = subparsers.add_parser("say", help="Speak text aloud using native speech synthesis")
    say_parser.add_argument("text", nargs="+", help="Text to speak")

    # Exclusive Killer Suite
    write_parser = subparsers.add_parser("write", help="Ghostwriter: AI inline text transformation")
    write_parser.add_argument("--mode", default="polish", choices=["polish", "polite", "grammar", "summarize", "translate_en", "translate_ru", "code_explain", "code_fix"], help="Transformation mode")
    write_parser.add_argument("text", nargs="*", help="Optional text (if omitted, reads and rewrites clipboard)")

    vault_parser = subparsers.add_parser("vault", help="Memory Vault: Long-term cross-session user memory")
    vault_parser.add_argument("action", nargs="?", default="list", choices=["list", "remember", "forget"], help="Action")
    vault_parser.add_argument("key", nargs="?", help="Fact key")
    vault_parser.add_argument("value", nargs="*", help="Fact value")

    subparsers.add_parser("standup", help="Daily Standup & Commit Crafter: Generate ready-to-share report")

    sandbox_parser = subparsers.add_parser("sandbox", help="Terminal Sandbox Lens: inspect command safety")
    sandbox_parser.add_argument("command", nargs="+", help="Shell command to inspect")

    args, unknown = parser.parse_known_args()

    engine = GhostEngine()
    rag = ZeroDbRAG()

    if not args.subcommand:
        if unknown:
            cmd_ask(engine, rag, " ".join(unknown))
        else:
            cmd_pet()
        return

    if args.subcommand == "ask":
        cmd_ask(engine, rag, " ".join(args.query))
    elif args.subcommand == "chat":
        cmd_chat(engine, rag)
    elif args.subcommand == "pet":
        cmd_pet(skin=getattr(args, "skin", "glass"))
    elif args.subcommand == "models":
        cmd_models(engine)
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
    elif args.subcommand in {"clip", "clipboard"}:
        cmd_clip()
    elif args.subcommand in {"time", "timemachine"}:
        cmd_timemachine()
    elif args.subcommand == "rpg":
        cmd_rpg()
    elif args.subcommand == "chameleon":
        cmd_chameleon()
    elif args.subcommand == "web":
        cmd_web(" ".join(args.query))
    elif args.subcommand == "agent":
        cmd_agent(" ".join(args.task))
    elif args.subcommand == "say":
        cmd_say(" ".join(args.text))
    elif args.subcommand == "write":
        cmd_write(mode=args.mode, text=" ".join(args.text) if args.text else None)
    elif args.subcommand == "vault":
        val_str = " ".join(args.value) if args.value else None
        cmd_vault(action=args.action, key=args.key, value=val_str)
    elif args.subcommand == "standup":
        cmd_standup()
    elif args.subcommand == "sandbox":
        cmd_sandbox(" ".join(args.command))

if __name__ == "__main__":
    main()
