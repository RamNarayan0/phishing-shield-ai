#!/usr/bin/env python3
"""
Phishing Shield AI — MongoDB Duplicate Cleanup & Maintenance CLI
Usage:
    python cleanup_duplicates.py --dry-run
    python cleanup_duplicates.py --apply
    python cleanup_duplicates.py --backup-only
"""
import sys
import json
import argparse
from app.db.mongodb import init_db, is_connected, _collection, MONGODB_DATABASE, MONGODB_COLLECTION
from app.db.cleanup import clean_duplicates, create_backup

def main():
    parser = argparse.ArgumentParser(description="Safely inspect and clean duplicate phishing records and test clutter in MongoDB.")
    parser.add_argument("--apply", action="store_true", help="Apply cleanup deletions and canonical merges (default is dry-run).")
    parser.add_argument("--dry-run", action="store_true", help="Audit mode without making changes (default).")
    parser.add_argument("--cross-source", action="store_true", help="Merge identical message content across different sources.")
    parser.add_argument("--keep-test-artifacts", action="store_true", help="Do not purge automated test artifacts.")
    parser.add_argument("--backup-only", action="store_true", help="Create an immediate point-in-time snapshot of the database collection without running cleanup.")
    args = parser.parse_args()

    is_dry_run = not args.apply

    print("=" * 65)
    print("PHISHING SHIELD AI — DATABASE AUDIT & DUPLICATE CLEANUP")
    print("=" * 65)

    if not is_connected():
        print("Connecting to MongoDB...")
        success = init_db()
        if not success or not is_connected():
            print("\n[ERROR] Could not connect to MongoDB.")
            print("Ensure local MongoDB is running at mongodb://127.0.0.1:27017 or check MONGODB_URI.")
            sys.exit(1)

    print(f"Target Database   : {MONGODB_DATABASE}")
    print(f"Target Collection : {MONGODB_COLLECTION}")

    if args.backup_only:
        print("\nExecuting immediate snapshot backup...")
        backup_res = create_backup(_collection)
        print(json.dumps(backup_res, indent=2))
        return

    print(f"Execution Mode    : {'DRY RUN (Audit only - no records will be modified/deleted)' if is_dry_run else 'APPLY (Automatic backup will be created, redundant duplicates merged)'}")
    print(f"Cross-Source Merge: {args.cross_source}")
    print(f"Purge Test Clutter: {not args.keep_test_artifacts}\n")

    report = clean_duplicates(
        _collection,
        dry_run=is_dry_run,
        cross_source=args.cross_source,
        purge_test_artifacts=not args.keep_test_artifacts
    )
    print(json.dumps(report, indent=2))

    if is_dry_run:
        total_ident = report.get("redundant_records_identified", 0) + report.get("test_artifacts_identified", 0)
        if total_ident > 0:
            print(f"\n[AUDIT SUMMARY] Found {report['test_artifacts_identified']} test artifacts and {report['redundant_records_identified']} redundant records across {report['duplicate_groups_found']} duplicate groups.")
            print("To safely apply these changes (which automatically generates a backup first), run:")
            print("       python cleanup_duplicates.py --apply")

if __name__ == "__main__":
    main()
