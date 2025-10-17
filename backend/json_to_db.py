"""
Import diary entries from JSON files to database.

Usage:
    python json_to_db.py [json_directory]
    
Example:
    python json_to_db.py data/json
    python json_to_db.py  # defaults to data/json
"""
import json
import os
import sys
from database import DiaryDatabase


def import_json_to_db(json_dir: str = "../data/json"):
    """Import all JSON files from directory to database."""
    
    if not os.path.exists(json_dir):
        print(f"Error: Directory '{json_dir}' not found")
        return
    
    db = DiaryDatabase()
    
    total_entries = 0
    new_entries = 0
    duplicate_entries = 0
    
    print("=" * 60)
    print("Importing JSON files to database...")
    print("=" * 60)
    
    # Walk through all JSON files
    for root, dirs, files in os.walk(json_dir):
        for filename in files:
            if not filename.endswith('.json'):
                continue
            
            filepath = os.path.join(root, filename)
            
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                date = data.get('date')
                entries = data.get('entries', [])
                
                if not date or not entries:
                    continue
                
                print(f"Processing {filepath}...")
                
                for content in entries:
                    total_entries += 1
                    entry_id = db.insert_diary(date, content)
                    
                    if entry_id:
                        new_entries += 1
                    else:
                        duplicate_entries += 1
                
            except Exception as e:
                print(f"  Error processing {filepath}: {str(e)}")
                continue
    
    print(f"\n" + "=" * 60)
    print("Import complete!")
    print(f"  Total entries processed: {total_entries}")
    print(f"  New entries added: {new_entries}")
    print(f"  Duplicates skipped: {duplicate_entries}")
    
    # Show statistics
    stats = db.get_statistics()
    print(f"\nDatabase Statistics:")
    print(f"  Total entries in DB: {stats['total']}")
    print(f"  Date range: {stats['date_range']['first_date']} to {stats['date_range']['last_date']}")
    print(f"  Months covered: {len(stats['monthly_counts'])}")
    print("=" * 60)


def main():
    """Main function."""
    json_dir = sys.argv[1] if len(sys.argv) > 1 else "data/json"
    import_json_to_db(json_dir)


if __name__ == "__main__":
    main()

