"""Interactive Command-Line Interface for Contract Compliance Checker."""

import os
import sys
import json

# Ensure root directory is on sys.path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from main_agent import MainAgent
from core.observability import get_event_logs

def print_header():
    print("\n" + "=" * 70)
    print("      AI CONTRACT COMPLIANCE & RISK AUDITOR (MULTI-AGENT)      ")
    print("=" * 70)

def print_menu():
    print("\nSelect an option:")
    print("  [1] Analyze Contract from Text Input")
    print("  [2] Analyze Contract from File Path (.txt, .md, .json, .pdf, .docx)")
    print("  [3] Run Quick Sample Contract (NDA, MSA, DPA, Employment)")
    print("  [4] Export Audit Report (Markdown / JSON)")
    print("  [5] View Multi-Agent Observability Logs / A2A Events")
    print("  [6] Launch Local Web Dashboard")
    print("  [7] Exit")

def run_sample_selector(agent: MainAgent):
    samples_dir = os.path.join(BASE_DIR, "sample_contracts")
    if not os.path.exists(samples_dir):
        print("Sample contracts directory not found.")
        return None

    files = [f for f in os.listdir(samples_dir) if f.endswith(".txt")]
    if not files:
        print("No sample files found.")
        return None

    print("\nAvailable Sample Contracts:")
    for idx, f in enumerate(files, 1):
        print(f"  [{idx}] {f}")

    choice = input("\nEnter choice (number): ").strip()
    try:
        idx = int(choice) - 1
        if 0 <= idx < len(files):
            selected_path = os.path.join(samples_dir, files[idx])
            print(f"\nAnalyzing: {files[idx]} ...")
            return agent.analyze_file(selected_path)
        else:
            print("Invalid selection.")
    except ValueError:
        print("Please enter a valid number.")
    return None

def interactive_cli():
    print_header()
    agent = MainAgent()
    last_result = None

    while True:
        print_menu()
        choice = input("\nEnter choice [1-7]: ").strip()

        if choice == "1":
            print("\nEnter/Paste your contract text (enter 'END' on a new line when done):")
            lines = []
            while True:
                line = input()
                if line.strip() == "END":
                    break
                lines.append(line)
            raw_text = "\n".join(lines).strip()
            if not raw_text:
                print("No text provided.")
                continue
            print("\nAnalyzing contract across Planner, Worker, and Evaluator agents...")
            last_result = agent.handle_message(raw_text)
            print("\n" + last_result["response"])

        elif choice == "2":
            file_path = input("\nEnter path to contract file: ").strip().strip('"').strip("'")
            if not os.path.exists(file_path):
                print(f"File not found: {file_path}")
                continue
            print("\nAnalyzing contract file...")
            last_result = agent.analyze_file(file_path)
            print("\n" + last_result["response"])

        elif choice == "3":
            last_result = run_sample_selector(agent)
            if last_result:
                print("\n" + last_result["response"])

        elif choice == "4":
            if not last_result:
                print("No analysis result available yet. Please run an analysis first.")
                continue
            export_fmt = input("Export format: [M]arkdown or [J]SON? (default: M): ").strip().upper()
            default_name = f"contract_audit_{last_result.get('session_id', 'report')[:8]}"
            
            if export_fmt == "J":
                filename = input(f"Enter filename (default: {default_name}.json): ").strip() or f"{default_name}.json"
                with open(filename, "w", encoding="utf-8") as f:
                    json.dump(last_result, f, indent=2)
                print(f"Report exported to {os.path.abspath(filename)}")
            else:
                filename = input(f"Enter filename (default: {default_name}.md): ").strip() or f"{default_name}.md"
                with open(filename, "w", encoding="utf-8") as f:
                    f.write(last_result.get("markdown_report", ""))
                print(f"Report exported to {os.path.abspath(filename)}")

        elif choice == "5":
            sid = last_result.get("session_id") if last_result else None
            logs = get_event_logs(sid)
            print(f"\n--- Observability Event Logs ({len(logs)} recorded) ---")
            for log in logs:
                print(f"[{log['timestamp']}] [{log['agent']}] {log['event_type']} -> {json.dumps(log['payload'], default=str)}")

        elif choice == "6":
            print("\nStarting local Web UI on http://localhost:8080 ...")
            try:
                import web_app
                web_app.run_server(port=8080)
            except KeyboardInterrupt:
                print("\nWeb server stopped.")
            except Exception as e:
                print(f"Could not start web server: {e}")

        elif choice in ["7", "exit", "quit", "q"]:
            print("\nExiting Contract Compliance Checker. Goodbye!")
            break
        else:
            print("Invalid option. Please choose between 1 and 7.")

if __name__ == "__main__":
    interactive_cli()

