# Backend - caigeng Diary Archive

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Ensure `.env` file exists in the root directory with your Aliyun credentials:
```
accessKeyId=YOUR_ACCESS_KEY_ID
accessKeySecret=YOUR_ACCESS_KEY_SECRET
```

## Usage

### Step 1: Convert Text to JSON
Extract and parse diary entries from raw text files:

```bash
# Process individual files
python process_diaries.py raw/1.txt 437
python process_diaries.py raw/2.txt
python process_diaries.py raw/3.txt
```

This will:
- Parse the specified text file starting from the given line
- Extract diary entries with dates
- Save to JSON files in `data/json/` (organized by year/month/day)
- Automatically skip duplicates

**Note**: The script follows KISS principle - it only reads the file you specify and converts it to JSON. Run it multiple times for multiple files.

### Step 2: Import JSON to Database
Import all JSON files into the database:

```bash
python json_to_db.py
# or specify custom path
python json_to_db.py data/json
```

This will:
- Read all JSON files from `data/json/`
- Insert entries into SQLite database (`data/diaries.db`)
- Automatically skip duplicates based on (date, content)

### Step 3: Run Sentiment Analysis (Optional)
Analyze sentiment for all diary entries:

```bash
python sentiment_api.py
```

This will:
- Call Aliyun NLP API for each entry without sentiment
- Store sentiment results in database
- Handle rate limiting automatically

### Step 4: Start API Server
Run the FastAPI server:

```bash
python api.py
```

The API will be available at:
- API: http://localhost:8000
- Documentation: http://localhost:8000/docs

## Workflow

The data processing follows a simple pipeline:

```
Raw Text Files → JSON Files → Database → API
     ↓               ↓           ↓
process_diaries  json_to_db  sentiment_api
                              (optional)
```

**Benefits of this approach:**
- **Flexibility**: Process files one by one
- **Safety**: JSON files serve as intermediate backup
- **Modularity**: Each script has a single responsibility
- **Reliability**: Duplicate detection at both JSON and DB levels

## API Endpoints

### Get Diary Entries
```
GET /api/diaries?date=2025-06-22
GET /api/diaries?month=2025-06
GET /api/diaries?sentiment=正面
GET /api/diaries?limit=100&offset=0
```

### Get Statistics
```
GET /api/stats
```

### Get Available Dates
```
GET /api/dates
```

### Search Entries
```
GET /api/search?q=图书馆
```

### Get Random Entries
```
GET /api/random?count=5
```

## Database Schema

```sql
CREATE TABLE diaries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date DATE NOT NULL,
    content TEXT NOT NULL,
    sentiment VARCHAR(10),
    positive_prob REAL,
    negative_prob REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(date, content)
);
```

## Notes

- All dates are normalized to `2025-MM-DD` format
- Duplicate entries (same date + content) are automatically skipped
- JSON files serve as a backup and can be re-imported anytime
- The sentiment analysis API has rate limits. The script includes automatic retry logic and delays

