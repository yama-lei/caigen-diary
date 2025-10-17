"""
FastAPI backend server for the diary archive system.
"""
from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List
from pydantic import BaseModel
from database import DiaryDatabase
import uvicorn


# Initialize FastAPI app
app = FastAPI(
    title="caigeng Diary Archive API",
    description="API for accessing and filtering diary entries from Nanjing University library",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database
db = DiaryDatabase()


# Pydantic models
class DiaryEntry(BaseModel):
    id: int
    date: str
    content: str
    sentiment: Optional[str]
    positive_prob: Optional[float]
    negative_prob: Optional[float]
    created_at: str


class Statistics(BaseModel):
    total: int
    sentiment_distribution: dict
    date_range: dict
    monthly_counts: dict


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "caigeng Diary Archive API",
        "version": "1.0.0",
        "endpoints": {
            "/api/diaries": "Get diary entries with filters",
            "/api/stats": "Get statistics",
            "/api/dates": "Get available dates"
        }
    }


@app.get("/api/diaries", response_model=List[DiaryEntry])
async def get_diaries(
    date: Optional[str] = Query(None, description="Filter by date (YYYY-MM-DD)"),
    month: Optional[str] = Query(None, description="Filter by month (YYYY-MM)"),
    sentiment: Optional[str] = Query(None, description="Filter by sentiment (正面/负面/中性)"),
    limit: Optional[int] = Query(100, description="Maximum number of entries to return"),
    offset: Optional[int] = Query(0, description="Number of entries to skip")
):
    """
    Get diary entries with optional filters.
    
    - **date**: Filter by specific date (YYYY-MM-DD)
    - **month**: Filter by month (YYYY-MM)
    - **sentiment**: Filter by sentiment (正面, 负面, 中性)
    - **limit**: Maximum entries to return (default: 100)
    - **offset**: Pagination offset (default: 0)
    """
    try:
        if date:
            entries = db.get_entries_by_date(date)
        elif month:
            # Parse year and month
            year, month_num = map(int, month.split('-'))
            entries = db.get_entries_by_month(year, month_num)
        elif sentiment:
            entries = db.get_entries_by_sentiment(sentiment)
        else:
            entries = db.get_all_entries(limit=limit, offset=offset)
        
        return entries
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/stats", response_model=Statistics)
async def get_statistics():
    """
    Get overall statistics about diary entries.
    
    Returns:
    - Total number of entries
    - Sentiment distribution
    - Date range
    - Monthly entry counts
    """
    try:
        stats = db.get_statistics()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/dates")
async def get_available_dates():
    """
    Get all available dates with entry counts.
    """
    try:
        conn = db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT date, COUNT(*) as count
            FROM diaries
            GROUP BY date
            ORDER BY date DESC
        """)
        
        dates = [{"date": row["date"], "count": row["count"]} for row in cursor.fetchall()]
        conn.close()
        
        return dates
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/search")
async def search_diaries(
    q: str = Query(..., description="Search query"),
    limit: Optional[int] = Query(50, description="Maximum results")
):
    """
    Search diary entries by content.
    
    - **q**: Search query (required)
    - **limit**: Maximum results to return
    """
    try:
        conn = db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM diaries
            WHERE content LIKE ?
            ORDER BY date DESC
            LIMIT ?
        """, (f"%{q}%", limit))
        
        entries = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return entries
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/random")
async def get_random_entries(count: int = Query(5, description="Number of random entries")):
    """
    Get random diary entries.
    
    - **count**: Number of random entries to return (default: 5)
    """
    try:
        conn = db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM diaries
            ORDER BY RANDOM()
            LIMIT ?
        """, (count,))
        
        entries = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return entries
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def main():
    """Run the API server."""
    print("=" * 60)
    print("Starting caigeng Diary Archive API Server")
    print("=" * 60)
    print("API Documentation: http://localhost:8005/docs")
    print("=" * 60)
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8005,
        log_level="info"
    )


if __name__ == "__main__":
    main()

