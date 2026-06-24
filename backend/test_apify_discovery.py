#!/usr/bin/env python3
"""
Test Apify LinkedIn Discovery System.

This script triggers the LinkedIn discovery process and monitors progress.

BEFORE RUNNING:
1. Set APIFY_API_TOKEN in .env file
2. Ensure backend, worker, and beat services are running
3. Have at least $5 credit in Apify account (500 companies ≈ $3-5)

USAGE:
    python test_apify_discovery.py
"""

import requests
import time
import sys
from datetime import datetime

# Configuration
API_BASE = "http://localhost:8000/api"
LOGIN_EMAIL = "admin@abbk.tn"
LOGIN_PASSWORD = "admin123"


def login():
    """Get JWT token."""
    print("🔐 Logging in...")
    response = requests.post(
        f"{API_BASE}/auth/login",
        data={"username": LOGIN_EMAIL, "password": LOGIN_PASSWORD}
    )

    if response.status_code != 200:
        print(f"❌ Login failed: {response.text}")
        sys.exit(1)

    token = response.json()["access_token"]
    print(f"✅ Logged in successfully\n")
    return token


def check_apify_stats(token):
    """Check current Apify stats."""
    print("📊 Current Apify Statistics:")
    print("-" * 50)

    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{API_BASE}/apify/stats", headers=headers)

    if response.status_code == 200:
        stats = response.json()
        print(f"  Leads with LinkedIn URL: {stats['total_leads_with_linkedin_url']}")
        print(f"  Enriched with data:      {stats['total_enriched_with_linkedin_data']}")
        print(f"  With employee counts:    {stats['total_with_employee_counts']}")
        print(f"  Enrichment coverage:     {stats['enrichment_coverage']}")
    else:
        print(f"  ⚠️  Could not fetch stats: {response.text}")

    print()


def trigger_discovery(token):
    """Trigger LinkedIn discovery."""
    print("🚀 Triggering LinkedIn Discovery...")
    print("-" * 50)
    print("  Searching for: Tunisian engineering & manufacturing companies")
    print("  Expected results: 500+ companies")
    print("  Estimated time: 10-30 minutes")
    print()

    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(f"{API_BASE}/apify/discover", headers=headers)

    if response.status_code != 200:
        print(f"❌ Failed to trigger discovery: {response.text}")
        sys.exit(1)

    result = response.json()
    task_id = result["task_id"]

    print(f"✅ Discovery task started!")
    print(f"  Task ID: {task_id}")
    print(f"  Status URL: {result['check_status_at']}")
    print()

    return task_id


def monitor_task(token, task_id):
    """Monitor task progress."""
    print("⏳ Monitoring task progress...")
    print("-" * 50)

    headers = {"Authorization": f"Bearer {token}"}
    start_time = datetime.now()

    while True:
        response = requests.get(f"{API_BASE}/apify/status/{task_id}", headers=headers)

        if response.status_code != 200:
            print(f"  ⚠️  Could not check status: {response.text}")
            time.sleep(10)
            continue

        data = response.json()
        status = data["status"]
        elapsed = (datetime.now() - start_time).total_seconds()

        if status == "pending":
            print(f"  [{int(elapsed)}s] ⏸️  Pending... (waiting for worker)")
        elif status == "running":
            print(f"  [{int(elapsed)}s] 🔄 Running... (discovering companies)")
        elif status == "completed":
            print(f"\n✅ Task completed in {int(elapsed)} seconds!")
            print("-" * 50)
            result = data.get("result", {})
            print(f"  Companies discovered: {result.get('discovered_count', 0)}")
            print(f"  Keywords searched: {result.get('keywords_searched', 0)}")
            print(f"  Status: {result.get('status', 'unknown')}")
            print()
            return result
        elif status == "failed":
            print(f"\n❌ Task failed after {int(elapsed)} seconds")
            print(f"  Error: {data.get('error', 'Unknown error')}")
            print()
            return None
        else:
            print(f"  [{int(elapsed)}s] ❓ Status: {status}")

        time.sleep(10)  # Check every 10 seconds


def check_database(token):
    """Check database for new leads."""
    print("📊 Checking database for new leads...")
    print("-" * 50)

    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{API_BASE}/leads?limit=10&sort_by=created_at&sort_order=desc", headers=headers)

    if response.status_code == 200:
        data = response.json()
        print(f"  Total leads: {data['total']}")
        print(f"  Showing {len(data['leads'])} most recent:")
        print()

        for i, lead in enumerate(data['leads'][:5], 1):
            print(f"  {i}. {lead['company_name']}")
            print(f"     Sector: {lead.get('sector', 'Unknown')}")
            print(f"     City: {lead.get('city', 'Unknown')}")
            print(f"     Employees: {lead.get('employee_count', 'Unknown')}")
            print(f"     Created: {lead.get('created_at', 'Unknown')}")
            print()
    else:
        print(f"  ⚠️  Could not fetch leads: {response.text}")


def main():
    """Run the full test."""
    print()
    print("=" * 50)
    print("  APIFY LINKEDIN DISCOVERY TEST")
    print("=" * 50)
    print()

    # Step 1: Login
    token = login()

    # Step 2: Check current stats
    check_apify_stats(token)

    # Step 3: Ask for confirmation
    print("⚠️  WARNING: This will consume Apify credits!")
    print("   Estimated cost: $3-5 for 500 companies")
    print()
    confirm = input("  Continue? (yes/no): ").strip().lower()

    if confirm != "yes":
        print("\n❌ Aborted by user")
        sys.exit(0)

    print()

    # Step 4: Trigger discovery
    task_id = trigger_discovery(token)

    # Step 5: Monitor progress
    result = monitor_task(token, task_id)

    # Step 6: Check database
    if result and result.get('discovered_count', 0) > 0:
        check_database(token)
        check_apify_stats(token)

    print("=" * 50)
    print("  TEST COMPLETE")
    print("=" * 50)
    print()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
