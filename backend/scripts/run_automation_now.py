#!/usr/bin/env python3
"""
Manually trigger the complete automation pipeline NOW.

This runs all 6 steps:
1. Discover companies from directories
2. Find websites via Google search
3. Scrape all company websites
4. Search job boards for hiring signals
5. Search news sites for company mentions
6. Recalculate all scores

Usage:
    python backend/scripts/run_automation_now.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.workers.tasks.complete_automation import run_complete_pipeline

if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("🚀 MANUAL TRIGGER: Complete Automation Pipeline")
    print("=" * 80)
    print("\nThis will:")
    print("  1. Discover companies from directories")
    print("  2. Find websites via Google search")
    print("  3. Scrape all company websites for signals")
    print("  4. Search job boards (emploi.tn) for hiring signals")
    print("  5. Search news sites (businessnews.com.tn) for mentions")
    print("  6. Recalculate all scores")
    print("\nStarting in 3 seconds...\n")

    import time
    time.sleep(3)

    result = run_complete_pipeline()

    print("\n" + "=" * 80)
    print("✅ AUTOMATION COMPLETE")
    print("=" * 80)
    print(f"\nResults: {result}\n")
