"""
Standalone script to run lead enrichment.

Detects:
- is_multinational
- is_exporter
- under_audit

For all existing leads in the database.
"""
import sys
import asyncio
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from app.workers.tasks.enrichment import detect_all_flags


async def main():
    print("=" * 70)
    print("ABBK LeadEngine — Lead Enrichment")
    print("=" * 70)
    print("\nDetecting high-value signals:")
    print("  • Multinational companies (international clients = must use licensed SW)")
    print("  • International exporters (audit pressure = must use licensed SW)")
    print("  • Companies under ISO/audit (cannot use cracked software)")
    print("\n" + "=" * 70)
    print()

    try:
        result = await detect_all_flags()

        print("\n" + "=" * 70)
        print("ENRICHMENT COMPLETE")
        print("=" * 70)
        print(f"\n📊 Results:")
        print(f"  Total leads processed: {result['total']}")
        print(f"  🏢 Multinational:       {result['multinational']} detected")
        print(f"  🌍 Exporters:           {result['exporter']} detected")
        print(f"  ✅ Under Audit:         {result['under_audit']} detected")
        print(f"  📝 Total updated:       {result['updated']} leads")
        print()

        if result['updated'] > 0:
            print("✅ Enrichment successful!")
            print("\nThese are ABBK's highest converting leads:")
            print("  • Multinationals MUST use licensed software (international clients)")
            print("  • Exporters MUST pass audits (cannot use cracked versions)")
            print("  • Under audit = ready to buy NOW")
        else:
            print("ℹ️  No new flags detected")
            print("   (All leads may already be enriched)")

        print("\n" + "=" * 70)

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    asyncio.run(main())
