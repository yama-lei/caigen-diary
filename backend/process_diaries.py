"""
Data processing script to extract and parse diary entries from raw text files.
Converts text files to JSON format with duplicate detection.

Usage:
    python process_diaries.py <file_path> [start_line]
    
Example:
    python process_diaries.py raw/1.txt 437
    python process_diaries.py raw/2.txt
"""
import re
import json
import os
import sys
from datetime import datetime
from typing import List, Tuple, Optional, Dict


class DiaryProcessor:
    def __init__(self, year: int = 2025):
        self.current_year = year
        
    def parse_date(self, date_str: str) -> Optional[str]:
        """
        Parse various date formats and return YYYY-MM-DD format.
        
        Supported formats:
        - 6.22, 6.23
        - 0805, 0814 (MMDD)
        - 2025.6.22
        """
        date_str = date_str.strip()
        
        # Pattern 1: M.D or MM.DD (e.g., 6.22, 06.22)
        match = re.match(r'^(\d{1,2})\.(\d{1,2})$', date_str)
        if match:
            month, day = int(match.group(1)), int(match.group(2))
            try:
                date_obj = datetime(self.current_year, month, day)
                return date_obj.strftime('%Y-%m-%d')
            except ValueError:
                return None
        
        # Pattern 2: MMDD (e.g., 0805, 1225)
        match = re.match(r'^(\d{2})(\d{2})$', date_str)
        if match:
            month, day = int(match.group(1)), int(match.group(2))
            try:
                date_obj = datetime(self.current_year, month, day)
                return date_obj.strftime('%Y-%m-%d')
            except ValueError:
                return None
        
        # Pattern 3: YYYY.M.D or YYYY.MM.DD
        match = re.match(r'^(\d{4})\.(\d{1,2})\.(\d{1,2})$', date_str)
        if match:
            year, month, day = int(match.group(1)), int(match.group(2)), int(match.group(3))
            try:
                date_obj = datetime(year, month, day)
                return date_obj.strftime('%Y-%m-%d')
            except ValueError:
                return None
        
        return None
    
    def extract_date_from_line(self, line: str) -> Optional[str]:
        """Extract date from a line of text."""
        line = line.strip()
        
        # Direct date at start of line
        match = re.match(r'^([\d\.]+)', line)
        if match:
            date_str = match.group(1)
            parsed = self.parse_date(date_str)
            if parsed:
                return parsed
        
        # "今天是X月X号" pattern
        match = re.search(r'今天是(\d{1,2})月(\d{1,2})号', line)
        if match:
            month, day = int(match.group(1)), int(match.group(2))
            try:
                date_obj = datetime(self.current_year, month, day)
                return date_obj.strftime('%Y-%m-%d')
            except ValueError:
                pass
        
        return None
    
    def parse_file(self, filepath: str, start_line: int = 1) -> List[Tuple[str, str]]:
        """
        Parse a text file and extract diary entries.
        
        Returns:
            List of tuples (date, content)
        """
        entries = []
        current_date = None
        current_content_lines = []
        
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Start from the specified line (1-indexed)
        lines = lines[start_line - 1:]
        
        for line in lines:
            line = line.rstrip('\n')
            
            # Try to extract a date from this line
            date = self.extract_date_from_line(line)
            
            if date:
                # Save previous entry if exists
                if current_date and current_content_lines:
                    for content in current_content_lines:
                        if content.strip():
                            entries.append((current_date, content.strip()))
                
                # Start new date
                current_date = date
                current_content_lines = []
                
                # Check if there's content on the same line after the date
                remaining = re.sub(r'^[\d\.]+\s*', '', line).strip()
                if remaining:
                    current_content_lines.append(remaining)
            else:
                # This line is content for the current date
                if current_date and line.strip():
                    current_content_lines.append(line.strip())
        
        # Don't forget the last entry
        if current_date and current_content_lines:
            for content in current_content_lines:
                if content.strip():
                    entries.append((current_date, content.strip()))
        
        return entries
    
    def load_existing_json(self, json_path: str) -> Dict:
        """Load existing JSON file or return empty structure."""
        if os.path.exists(json_path):
            with open(json_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {"date": "", "entries": []}
    
    def save_to_json(self, entries: List[Tuple[str, str]], output_dir: str = "data/json"):
        """
        Save entries to JSON files organized by date with duplicate detection.
        """
        # Group by date
        grouped = {}
        for date, content in entries:
            if date not in grouped:
                grouped[date] = []
            grouped[date].append(content)
        
        new_count = 0
        duplicate_count = 0
        
        # Write to JSON files
        for date, contents in grouped.items():
            date_obj = datetime.strptime(date, '%Y-%m-%d')
            year = date_obj.year
            month = date_obj.month
            day = date_obj.day
            
            # Create directory structure
            dir_path = f"{output_dir}/{year}/{month:02d}"
            os.makedirs(dir_path, exist_ok=True)
            
            file_path = f"{dir_path}/{day:02d}.json"
            
            # Load existing entries
            existing_data = self.load_existing_json(file_path)
            existing_entries = set(existing_data.get("entries", []))
            
            # Add only new entries (no duplicates)
            for content in contents:
                if content not in existing_entries:
                    existing_data["entries"] = existing_data.get("entries", [])
                    existing_data["entries"].append(content)
                    existing_entries.add(content)
                    new_count += 1
                else:
                    duplicate_count += 1
            
            # Update date field
            existing_data["date"] = date
            
            # Write back to file
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(existing_data, f, ensure_ascii=False, indent=2)
        
        return new_count, duplicate_count


def main():
    """Main processing function."""
    if len(sys.argv) < 2:
        print("Usage: python process_diaries.py <file_path> [start_line]")
        print("\nExample:")
        print("  python process_diaries.py raw/1.txt 437")
        print("  python process_diaries.py raw/2.txt")
        sys.exit(1)
    
    filepath = sys.argv[1]
    start_line = int(sys.argv[2]) if len(sys.argv) > 2 else 1
    
    if not os.path.exists(filepath):
        print(f"Error: File '{filepath}' not found")
        sys.exit(1)
    
    print("=" * 60)
    print("caigeng Diary Archive - Text to JSON Converter")
    print("=" * 60)
    print(f"Input file: {filepath}")
    print(f"Start line: {start_line}")
    print()
    
    processor = DiaryProcessor()
    
    # Parse file
    print("Parsing file...")
    entries = processor.parse_file(filepath, start_line)
    print(f"  Extracted {len(entries)} entries")
    
    # Save to JSON
    print("\nSaving to JSON files...")
    new_count, duplicate_count = processor.save_to_json(entries)
    
    print(f"\n" + "=" * 60)
    print("Processing complete!")
    print(f"  New entries added: {new_count}")
    print(f"  Duplicates skipped: {duplicate_count}")
    print("=" * 60)


if __name__ == "__main__":
    main()

