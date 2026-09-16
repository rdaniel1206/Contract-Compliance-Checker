"""Demo script showcasing multi-agent contract compliance analysis."""

import os
import sys

# Ensure root directory is on sys.path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from main_agent import MainAgent
from core.observability import get_event_logs

def run_demo():
    print("=" * 70)
    print("   AI MULTI-AGENT CONTRACT COMPLIANCE & RISK CHECKER DEMO")
    print("=" * 70)
    
    agent = MainAgent()
    samples_dir = os.path.join(BASE_DIR, "sample_contracts")
    
    sample_files = [
        ("Standard Balanced NDA", os.path.join(samples_dir, "sample_nda_standard.txt")),
        ("High-Risk Vendor MSA", os.path.join(samples_dir, "sample_vendor_msa_risky.txt")),
        ("GDPR Compliant DPA", os.path.join(samples_dir, "sample_dpa_standard.txt")),
        ("Employment Agreement (Non-Compete)", os.path.join(samples_dir, "sample_employment_agreement.txt")),
    ]

    for label, filepath in sample_files:
        if not os.path.exists(filepath):
            continue
        print(f"\n[DEMO] Analyzing Contract: {label}")
        print(f"       File: {os.path.basename(filepath)}")
        print("-" * 70)
        
        result = agent.analyze_file(filepath)
        print(result["response"])
        print("-" * 70)
        print(f"Risk Score: {result['meta']['score']} | Rating: {result['meta']['level']}")
        if result['meta']['red_flags']:
            print(f"Identified Red Flags: {len(result['meta']['red_flags'])}")
            for rf in result['meta']['red_flags']:
                print(f"  [!] {rf}")
        print("=" * 70)

    print(f"\n[OBSERVABILITY] Total Log Events Recorded: {len(get_event_logs())}")
    print("Demo completed successfully!")

if __name__ == "__main__":
    run_demo()

