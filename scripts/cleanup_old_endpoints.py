"""
Cleanup Old SageMaker Endpoints
Deletes all but the most recent endpoint to free up instance quota
"""

import boto3
import sys
from datetime import datetime

def cleanup_old_endpoints(region='us-east-1', keep_latest=1, dry_run=False):
    """
    Delete old endpoints to free up quota
    
    Args:
        region: AWS region
        keep_latest: Number of recent endpoints to keep (default: 1)
        dry_run: If True, only show what would be deleted without actually deleting
    """
    client = boto3.client('sagemaker', region_name=region)
    
    print(f"🔍 Listing endpoints in {region}...")
    response = client.list_endpoints(
        SortBy='CreationTime',
        SortOrder='Descending',
        StatusEquals='InService'
    )
    
    endpoints = response['Endpoints']
    print(f"\n✅ Found {len(endpoints)} InService endpoints")
    
    if len(endpoints) <= keep_latest:
        print(f"✓ Only {len(endpoints)} endpoint(s) exist. Nothing to delete.")
        return
    
    # Keep the latest N, delete the rest
    endpoints_to_keep = endpoints[:keep_latest]
    endpoints_to_delete = endpoints[keep_latest:]
    
    print(f"\n📌 KEEPING (latest {keep_latest}):")
    for ep in endpoints_to_keep:
        print(f"  ✓ {ep['EndpointName']} (Created: {ep['CreationTime']})")
    
    print(f"\n🗑️  TO DELETE ({len(endpoints_to_delete)} endpoints):")
    for ep in endpoints_to_delete:
        print(f"  ✗ {ep['EndpointName']} (Created: {ep['CreationTime']})")
    
    if dry_run:
        print("\n⚠️  DRY RUN - No endpoints were deleted")
        print("   Run without --dry-run to actually delete")
        return
    
    # Confirm deletion
    print(f"\n⚠️  This will delete {len(endpoints_to_delete)} endpoints and free up quota")
    confirm = input("Continue? (yes/no): ")
    
    if confirm.lower() != 'yes':
        print("❌ Cancelled by user")
        return
    
    print("\n🔥 Deleting endpoints...")
    deleted_count = 0
    
    for ep in endpoints_to_delete:
        endpoint_name = ep['EndpointName']
        try:
            print(f"  Deleting {endpoint_name}...", end=' ')
            client.delete_endpoint(EndpointName=endpoint_name)
            print("✓")
            deleted_count += 1
        except Exception as e:
            print(f"✗ Error: {e}")
    
    print(f"\n✅ Successfully deleted {deleted_count}/{len(endpoints_to_delete)} endpoints")
    print(f"💰 Freed up {deleted_count} ml.m5.large instances from quota")
    
    # Also cleanup failed endpoints
    print("\n🧹 Cleaning up failed endpoints...")
    failed_response = client.list_endpoints(StatusEquals='Failed')
    failed_endpoints = failed_response['Endpoints']
    
    if failed_endpoints:
        print(f"   Found {len(failed_endpoints)} failed endpoints to clean up:")
        for ep in failed_endpoints:
            endpoint_name = ep['EndpointName']
            try:
                print(f"  Deleting {endpoint_name}...", end=' ')
                client.delete_endpoint(EndpointName=endpoint_name)
                print("✓")
            except Exception as e:
                print(f"✗ Error: {e}")
    else:
        print("   No failed endpoints to clean up")
    
    print("\n✅ Cleanup complete!")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Cleanup old SageMaker endpoints')
    parser.add_argument('--region', default='us-east-1', help='AWS region (default: us-east-1)')
    parser.add_argument('--keep', type=int, default=1, help='Number of recent endpoints to keep (default: 1)')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be deleted without actually deleting')
    
    args = parser.parse_args()
    
    cleanup_old_endpoints(
        region=args.region,
        keep_latest=args.keep,
        dry_run=args.dry_run
    )
