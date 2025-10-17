"""
Aliyun NLP API integration for sentiment analysis.
"""
import json
import time
import hmac
import hashlib
import base64
import uuid
from datetime import datetime
from urllib.parse import quote
import requests
from typing import Dict, Optional
from database import DiaryDatabase
import os
from dotenv import load_dotenv


class AliyunSentimentAnalyzer:
    def __init__(self):
        # Load environment variables
        load_dotenv()
        self.access_key_id = os.getenv('accessKeyId')
        self.access_key_secret = os.getenv('accessKeySecret')
        
        if not self.access_key_id or not self.access_key_secret:
            raise ValueError("Missing Aliyun credentials in .env file")
        
        self.endpoint = "https://alinlp.cn-hangzhou.aliyuncs.com/"
        self.db = DiaryDatabase()
    
    def _generate_signature(self, params: Dict[str, str], method: str = "POST") -> str:
        """Generate signature for Aliyun API request."""
        # Sort parameters
        sorted_params = sorted(params.items())
        
        # Build canonical query string
        canonical_query_string = "&".join([
            f"{quote(k, safe='')}={quote(str(v), safe='')}"
            for k, v in sorted_params
        ])
        
        # Build string to sign
        string_to_sign = (
            f"{method}&{quote('/', safe='')}&"
            f"{quote(canonical_query_string, safe='')}"
        )
        
        # Calculate signature
        key = (self.access_key_secret + "&").encode('utf-8')
        signature = hmac.new(
            key,
            string_to_sign.encode('utf-8'),
            hashlib.sha1
        ).digest()
        
        return base64.b64encode(signature).decode('utf-8')
    
    def analyze_sentiment(self, text: str, retry_count: int = 3) -> Optional[Dict]:
        """
        Analyze sentiment of a text using Aliyun NLP API.
        
        Args:
            text: Text to analyze (max 1000 characters)
            retry_count: Number of retries for rate limiting
            
        Returns:
            Dict with sentiment, positive_prob, negative_prob, or None if error
        """
        # Truncate text if too long
        if len(text) > 1000:
            text = text[:1000]
        
        # Common parameters
        timestamp = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
        nonce = str(uuid.uuid4())
        
        params = {
            'Action': 'GetSaChGeneral',
            'ServiceCode': 'alinlp',
            'Text': text,
            'Format': 'JSON',
            'Version': '2020-06-29',
            'AccessKeyId': self.access_key_id,
            'SignatureMethod': 'HMAC-SHA1',
            'Timestamp': timestamp,
            'SignatureVersion': '1.0',
            'SignatureNonce': nonce,
        }
        
        # Generate signature
        signature = self._generate_signature(params)
        params['Signature'] = signature
        
        # Make request
        for attempt in range(retry_count):
            try:
                response = requests.post(
                    self.endpoint,
                    data=params,
                    timeout=30
                )
                
                if response.status_code == 200:
                    result = response.json()
                    
                    # Parse response
                    if 'Data' in result:
                        data = json.loads(result['Data'])
                        if data.get('success'):
                            sentiment_result = data['result']
                            return {
                                'sentiment': sentiment_result['sentiment'],
                                'positive_prob': sentiment_result['positive_prob'],
                                'negative_prob': sentiment_result['negative_prob']
                            }
                    
                    return None
                
                elif response.status_code == 429:
                    # Rate limiting - wait and retry
                    wait_time = (attempt + 1) * 2
                    print(f"  Rate limited, waiting {wait_time}s...")
                    time.sleep(wait_time)
                    continue
                
                else:
                    print(f"  API error: {response.status_code} - {response.text}")
                    return None
                    
            except Exception as e:
                print(f"  Request error: {str(e)}")
                if attempt < retry_count - 1:
                    time.sleep(2)
                    continue
                return None
        
        return None
    def process_all_entries(self, batch_size: int = 10, delay: float = 0.5):
        """
        Process all diary entries without sentiment analysis.
        
        Args:
            batch_size: Number of entries to process before showing progress
            delay: Delay between requests in seconds
        """
        # Get entries without sentiment
        entries = self.db.get_entries_without_sentiment()
        
        if not entries:
            print("No entries to process!")
            return
        
        total = len(entries)
        print(f"Processing sentiment analysis for {total} entries...")
        print("=" * 60)
        
        success_count = 0
        error_count = 0
        
        for idx, entry in enumerate(entries, 1):
            entry_id = entry['id']
            content = entry['content']
            
            # Show progress
            if idx % batch_size == 0 or idx == total:
                print(f"Progress: {idx}/{total} ({idx/total*100:.1f}%)")
            
            # Analyze sentiment
            result = self.analyze_sentiment(content)
            
            if result:
                # Update database
                self.db.update_sentiment(
                    entry_id,
                    result['sentiment'],
                    result['positive_prob'],
                    result['negative_prob']
                )
                success_count += 1
            else:
                error_count += 1
                print(f"  Failed to analyze entry {entry_id}")
            
            # Delay to avoid rate limiting
            time.sleep(delay)
        
        print("=" * 60)
        print(f"Sentiment analysis complete!")
        print(f"  Success: {success_count}")
        print(f"  Errors: {error_count}")
        
        # Show sentiment distribution
        stats = self.db.get_statistics()
        if stats['sentiment_distribution']:
            print(f"\nSentiment Distribution:")
            for sentiment, count in stats['sentiment_distribution'].items():
                print(f"  {sentiment}: {count} ({count/total*100:.1f}%)")


def main():
    """Main function to run sentiment analysis."""
    print("=" * 60)
    print("caigeng Diary Archive - Sentiment Analysis")
    print("=" * 60)
    
    try:
        analyzer = AliyunSentimentAnalyzer()
        analyzer.process_all_entries(batch_size=10, delay=0.5)
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

