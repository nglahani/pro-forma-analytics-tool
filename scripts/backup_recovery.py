"""
Database Backup and Recovery System

Provides automated backup creation, validation, and recovery procedures
for the pro-forma analytics SQLite databases.
"""

import os
import sys
import shutil
import sqlite3
import argparse
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import logging
import hashlib
import gzip

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.logging_config import get_logger


class DatabaseBackupManager:
    """Manages database backups and recovery operations."""
    
    def __init__(self, backup_dir: Optional[str] = None):
        self.logger = get_logger(__name__)
        self.project_root = Path(__file__).parent.parent
        self.db_dir = self.project_root / "data" / "databases"
        self.backup_dir = Path(backup_dir) if backup_dir else self.db_dir / "backups"
        
        # Ensure directories exist
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        # Database files to manage
        self.databases = {
            'market_data': self.db_dir / 'market_data.db',
            'property_data': self.db_dir / 'property_data.db',
            'economic_data': self.db_dir / 'economic_data.db',
            'forecast_cache': self.db_dir / 'forecast_cache.db'
        }
        
        # Backup retention policy (days)
        self.retention_policy = {
            'daily': 7,      # Keep daily backups for 7 days
            'weekly': 30,    # Keep weekly backups for 30 days  
            'monthly': 365   # Keep monthly backups for 1 year
        }
    
    def create_backup(self, backup_type: str = 'manual', 
                     compress: bool = True, 
                     verify: bool = True) -> Dict[str, any]:
        """Create backup of all databases."""
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_info = {
            'timestamp': timestamp,
            'backup_type': backup_type,
            'created_at': datetime.now().isoformat(),
            'databases': {},
            'compressed': compress,
            'verified': False,
            'total_size_mb': 0
        }
        
        self.logger.info(f"Creating {backup_type} backup at {timestamp}")
        
        try:
            total_size = 0
            
            for db_name, db_path in self.databases.items():
                if not db_path.exists():
                    self.logger.warning(f"Database {db_name} not found at {db_path}")
                    continue
                
                # Create backup filename
                backup_filename = f"{db_name}_{backup_type}_{timestamp}.db"
                if compress:
                    backup_filename += ".gz"
                
                backup_path = self.backup_dir / backup_filename
                
                # Create backup
                if compress:
                    self._create_compressed_backup(db_path, backup_path)
                else:
                    shutil.copy2(db_path, backup_path)
                
                # Get file sizes
                original_size = db_path.stat().st_size
                backup_size = backup_path.stat().st_size
                total_size += backup_size
                
                # Calculate checksum
                checksum = self._calculate_checksum(db_path)
                
                backup_info['databases'][db_name] = {
                    'original_path': str(db_path),
                    'backup_path': str(backup_path),
                    'original_size_bytes': original_size,
                    'backup_size_bytes': backup_size,
                    'compression_ratio': backup_size / original_size if compress else 1.0,
                    'checksum': checksum
                }
                
                self.logger.info(f"Backed up {db_name}: {original_size/1024/1024:.1f}MB -> {backup_size/1024/1024:.1f}MB")
            
            backup_info['total_size_mb'] = total_size / 1024 / 1024
            
            # Verify backups if requested
            if verify:
                backup_info['verified'] = self._verify_backup(backup_info)
            
            # Save backup metadata
            self._save_backup_metadata(backup_info)
            
            self.logger.info(f"Backup completed successfully: {len(backup_info['databases'])} databases, {backup_info['total_size_mb']:.1f}MB")
            
            return backup_info
            
        except Exception as e:
            self.logger.error(f"Backup failed: {e}")
            backup_info['error'] = str(e)
            return backup_info
    
    def _create_compressed_backup(self, source_path: Path, backup_path: Path):
        """Create a compressed backup of a database."""
        
        with open(source_path, 'rb') as f_in:
            with gzip.open(backup_path, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
    
    def _calculate_checksum(self, file_path: Path) -> str:
        """Calculate SHA256 checksum of a file."""
        
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    
    def _verify_backup(self, backup_info: Dict) -> bool:
        """Verify backup integrity."""
        
        self.logger.info("Verifying backup integrity...")
        
        try:
            for db_name, db_info in backup_info['databases'].items():
                backup_path = Path(db_info['backup_path'])
                
                # For compressed backups, decompress temporarily for verification
                if backup_path.suffix == '.gz':
                    temp_path = backup_path.with_suffix('')
                    with gzip.open(backup_path, 'rb') as f_in:
                        with open(temp_path, 'wb') as f_out:
                            shutil.copyfileobj(f_in, f_out)
                    verify_path = temp_path
                else:
                    verify_path = backup_path
                
                # Verify SQLite database integrity
                try:
                    conn = sqlite3.connect(verify_path)
                    cursor = conn.cursor()
                    cursor.execute("PRAGMA integrity_check")
                    result = cursor.fetchone()
                    conn.close()
                    
                    if result[0] != 'ok':
                        self.logger.error(f"Integrity check failed for {db_name}: {result[0]}")
                        return False
                        
                except Exception as e:
                    self.logger.error(f"Failed to verify {db_name}: {e}")
                    return False
                finally:
                    # Clean up temporary file
                    if backup_path.suffix == '.gz' and verify_path.exists():
                        verify_path.unlink()
            
            self.logger.info("Backup verification successful")
            return True
            
        except Exception as e:
            self.logger.error(f"Backup verification failed: {e}")
            return False
    
    def _save_backup_metadata(self, backup_info: Dict):
        """Save backup metadata to JSON file."""
        
        metadata_file = self.backup_dir / f"backup_metadata_{backup_info['timestamp']}.json"
        
        try:
            with open(metadata_file, 'w') as f:
                json.dump(backup_info, f, indent=2)
                
        except Exception as e:
            self.logger.error(f"Failed to save backup metadata: {e}")
    
    def list_backups(self, backup_type: Optional[str] = None) -> List[Dict]:
        """List available backups."""
        
        backups = []
        
        # Find all metadata files
        for metadata_file in self.backup_dir.glob("backup_metadata_*.json"):
            try:
                with open(metadata_file, 'r') as f:
                    backup_info = json.load(f)
                
                # Filter by backup type if specified
                if backup_type and backup_info.get('backup_type') != backup_type:
                    continue
                
                backups.append(backup_info)
                
            except Exception as e:
                self.logger.warning(f"Failed to read backup metadata {metadata_file}: {e}")
        
        # Sort by timestamp (newest first)
        backups.sort(key=lambda x: x['timestamp'], reverse=True)
        
        return backups
    
    def restore_backup(self, timestamp: str, 
                      databases: Optional[List[str]] = None,
                      create_backup_before_restore: bool = True) -> Dict[str, any]:
        """Restore databases from backup."""
        
        self.logger.info(f"Restoring backup from {timestamp}")
        
        restore_info = {
            'timestamp': timestamp,
            'restore_started_at': datetime.now().isoformat(),
            'databases_restored': {},
            'pre_restore_backup': None,
            'success': False
        }
        
        try:
            # Find backup metadata
            metadata_file = self.backup_dir / f"backup_metadata_{timestamp}.json"
            if not metadata_file.exists():
                raise ValueError(f"Backup metadata not found for timestamp {timestamp}")
            
            with open(metadata_file, 'r') as f:
                backup_info = json.load(f)
            
            # Create backup before restore if requested
            if create_backup_before_restore:
                self.logger.info("Creating pre-restore backup...")
                pre_restore_backup = self.create_backup('pre_restore', compress=True, verify=False)
                restore_info['pre_restore_backup'] = pre_restore_backup['timestamp']
            
            # Determine which databases to restore
            if databases is None:
                databases = list(backup_info['databases'].keys())
            
            # Restore each database
            for db_name in databases:
                if db_name not in backup_info['databases']:
                    self.logger.warning(f"Database {db_name} not found in backup")
                    continue
                
                db_info = backup_info['databases'][db_name]
                backup_path = Path(db_info['backup_path'])
                target_path = Path(db_info['original_path'])
                
                if not backup_path.exists():
                    self.logger.error(f"Backup file not found: {backup_path}")
                    continue
                
                # Restore database
                if backup_path.suffix == '.gz':
                    # Decompress backup
                    with gzip.open(backup_path, 'rb') as f_in:
                        with open(target_path, 'wb') as f_out:
                            shutil.copyfileobj(f_in, f_out)
                else:
                    shutil.copy2(backup_path, target_path)
                
                # Verify restored database
                try:
                    conn = sqlite3.connect(target_path)
                    cursor = conn.cursor()
                    cursor.execute("PRAGMA integrity_check")
                    result = cursor.fetchone()
                    conn.close()
                    
                    if result[0] != 'ok':
                        raise ValueError(f"Restored database integrity check failed: {result[0]}")
                    
                    restore_info['databases_restored'][db_name] = {
                        'backup_path': str(backup_path),
                        'restored_to': str(target_path), 
                        'size_bytes': target_path.stat().st_size,
                        'integrity_verified': True
                    }
                    
                    self.logger.info(f"Successfully restored {db_name}")
                    
                except Exception as e:
                    self.logger.error(f"Failed to verify restored database {db_name}: {e}")
                    restore_info['databases_restored'][db_name] = {
                        'backup_path': str(backup_path),
                        'restored_to': str(target_path),
                        'error': str(e),
                        'integrity_verified': False
                    }
            
            restore_info['success'] = len(restore_info['databases_restored']) > 0
            restore_info['restore_completed_at'] = datetime.now().isoformat()
            
            self.logger.info(f"Restore completed: {len(restore_info['databases_restored'])} databases restored")
            
            return restore_info
            
        except Exception as e:
            self.logger.error(f"Restore failed: {e}")
            restore_info['error'] = str(e)
            restore_info['restore_completed_at'] = datetime.now().isoformat()
            return restore_info
    
    def cleanup_old_backups(self) -> Dict[str, int]:
        """Clean up old backups according to retention policy."""
        
        self.logger.info("Cleaning up old backups...")
        
        cleanup_info = {
            'daily_removed': 0,
            'weekly_removed': 0,
            'monthly_removed': 0,
            'manual_removed': 0,
            'total_removed': 0,
            'space_freed_mb': 0
        }
        
        try:
            backups = self.list_backups()
            now = datetime.now()
            
            for backup_info in backups:
                backup_date = datetime.fromisoformat(backup_info['created_at'])
                backup_type = backup_info.get('backup_type', 'manual')
                age_days = (now - backup_date).days
                
                # Determine if backup should be removed
                should_remove = False
                
                if backup_type in self.retention_policy:
                    if age_days > self.retention_policy[backup_type]:
                        should_remove = True
                elif backup_type == 'manual' and age_days > 90:  # Keep manual backups for 90 days
                    should_remove = True
                
                if should_remove:
                    # Remove backup files
                    space_freed = 0
                    
                    for db_name, db_info in backup_info['databases'].items():
                        backup_path = Path(db_info['backup_path'])
                        if backup_path.exists():
                            space_freed += backup_path.stat().st_size
                            backup_path.unlink()
                    
                    # Remove metadata file
                    metadata_file = self.backup_dir / f"backup_metadata_{backup_info['timestamp']}.json"
                    if metadata_file.exists():
                        metadata_file.unlink()
                    
                    cleanup_info[f"{backup_type}_removed"] += 1
                    cleanup_info['total_removed'] += 1
                    cleanup_info['space_freed_mb'] += space_freed / 1024 / 1024
                    
                    self.logger.info(f"Removed {backup_type} backup from {backup_date.date()} ({age_days} days old)")
            
            self.logger.info(f"Cleanup completed: {cleanup_info['total_removed']} backups removed, {cleanup_info['space_freed_mb']:.1f}MB freed")
            
            return cleanup_info
            
        except Exception as e:
            self.logger.error(f"Backup cleanup failed: {e}")
            return cleanup_info
    
    def get_backup_status(self) -> Dict[str, any]:
        """Get comprehensive backup system status."""
        
        backups = self.list_backups()
        
        # Calculate statistics
        backup_types = {}
        total_size = 0
        
        for backup in backups:
            backup_type = backup.get('backup_type', 'unknown')
            if backup_type not in backup_types:
                backup_types[backup_type] = 0
            backup_types[backup_type] += 1
            total_size += backup.get('total_size_mb', 0)
        
        # Find most recent backup
        most_recent_backup = backups[0] if backups else None
        
        return {
            'backup_directory': str(self.backup_dir),
            'total_backups': len(backups),
            'backup_types': backup_types,
            'total_size_mb': total_size,
            'most_recent_backup': {
                'timestamp': most_recent_backup['timestamp'],
                'backup_type': most_recent_backup['backup_type'],
                'created_at': most_recent_backup['created_at'],
                'databases_count': len(most_recent_backup['databases']),
                'verified': most_recent_backup.get('verified', False)
            } if most_recent_backup else None,
            'databases_managed': list(self.databases.keys()),
            'retention_policy': self.retention_policy
        }


def main():
    parser = argparse.ArgumentParser(description='Database backup and recovery management')
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Backup command
    backup_parser = subparsers.add_parser('backup', help='Create database backup')
    backup_parser.add_argument('--type', default='manual', help='Backup type (manual, daily, weekly, monthly)')
    backup_parser.add_argument('--no-compress', action='store_true', help='Disable compression')
    backup_parser.add_argument('--no-verify', action='store_true', help='Skip verification')
    backup_parser.add_argument('--backup-dir', help='Custom backup directory')
    
    # Restore command
    restore_parser = subparsers.add_parser('restore', help='Restore from backup')
    restore_parser.add_argument('timestamp', help='Backup timestamp to restore')
    restore_parser.add_argument('--databases', nargs='+', help='Specific databases to restore')
    restore_parser.add_argument('--no-backup', action='store_true', help='Skip pre-restore backup')
    restore_parser.add_argument('--backup-dir', help='Custom backup directory')
    
    # List command
    list_parser = subparsers.add_parser('list', help='List available backups')
    list_parser.add_argument('--type', help='Filter by backup type')
    list_parser.add_argument('--backup-dir', help='Custom backup directory')
    
    # Cleanup command
    cleanup_parser = subparsers.add_parser('cleanup', help='Clean up old backups')
    cleanup_parser.add_argument('--backup-dir', help='Custom backup directory')
    
    # Status command
    status_parser = subparsers.add_parser('status', help='Show backup system status')
    status_parser.add_argument('--backup-dir', help='Custom backup directory')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Initialize backup manager
    backup_manager = DatabaseBackupManager(args.backup_dir if hasattr(args, 'backup_dir') else None)
    
    if args.command == 'backup':
        result = backup_manager.create_backup(
            backup_type=args.type,
            compress=not args.no_compress,
            verify=not args.no_verify
        )
        
        if 'error' in result:
            print(f"Backup failed: {result['error']}")
            sys.exit(1)
        else:
            print(f"Backup completed successfully:")
            print(f"  Timestamp: {result['timestamp']}")
            print(f"  Databases: {len(result['databases'])}")
            print(f"  Total size: {result['total_size_mb']:.1f}MB")
            print(f"  Verified: {result['verified']}")
    
    elif args.command == 'restore':
        result = backup_manager.restore_backup(
            timestamp=args.timestamp,
            databases=args.databases,
            create_backup_before_restore=not args.no_backup
        )
        
        if not result['success']:
            print(f"Restore failed: {result.get('error', 'Unknown error')}")
            sys.exit(1)
        else:
            print(f"Restore completed successfully:")
            print(f"  Databases restored: {len(result['databases_restored'])}")
            if result['pre_restore_backup']:
                print(f"  Pre-restore backup: {result['pre_restore_backup']}")
    
    elif args.command == 'list':
        backups = backup_manager.list_backups(args.type)
        
        if not backups:
            print("No backups found")
        else:
            print(f"Found {len(backups)} backups:")
            print(f"{'Timestamp':<20} {'Type':<12} {'Databases':<10} {'Size (MB)':<10} {'Verified'}")
            print("-" * 70)
            
            for backup in backups:
                print(f"{backup['timestamp']:<20} {backup['backup_type']:<12} "
                      f"{len(backup['databases']):<10} {backup['total_size_mb']:<10.1f} "
                      f"{'Yes' if backup.get('verified') else 'No'}")
    
    elif args.command == 'cleanup':
        result = backup_manager.cleanup_old_backups()
        
        print(f"Cleanup completed:")
        print(f"  Total backups removed: {result['total_removed']}")
        print(f"  Space freed: {result['space_freed_mb']:.1f}MB")
        
        for backup_type, count in result.items():
            if backup_type.endswith('_removed') and count > 0:
                print(f"  {backup_type.replace('_removed', '').title()} backups: {count}")
    
    elif args.command == 'status':
        status = backup_manager.get_backup_status()
        
        print("Backup System Status:")
        print(f"  Backup directory: {status['backup_directory']}")
        print(f"  Total backups: {status['total_backups']}")
        print(f"  Total size: {status['total_size_mb']:.1f}MB")
        print(f"  Databases managed: {', '.join(status['databases_managed'])}")
        
        if status['most_recent_backup']:
            recent = status['most_recent_backup']
            print(f"\n  Most recent backup:")
            print(f"    Timestamp: {recent['timestamp']}")
            print(f"    Type: {recent['backup_type']}")
            print(f"    Databases: {recent['databases_count']}")
            print(f"    Verified: {'Yes' if recent['verified'] else 'No'}")


if __name__ == '__main__':
    main()