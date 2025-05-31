#!/usr/bin/env python3
"""
Load test script for Shop Titans Text Classification API

Sends 1000 requests to the /classify endpoint with 10x concurrency
to test the performance and reliability of the deployed API.
"""

import asyncio
import aiohttp
import time
import statistics
from pathlib import Path
import argparse
from typing import List, Dict, Any
import json

# Default configuration
DEFAULT_URL = "https://st-api.geostyx.com/classify"
DEFAULT_TOTAL_REQUESTS = 1000
DEFAULT_CONCURRENCY = 10
DEFAULT_IMAGE_PATH = "data/image.png"

class LoadTestResults:
    """Class to track and analyze load test results"""
    
    def __init__(self):
        self.response_times: List[float] = []
        self.status_codes: List[int] = []
        self.errors: List[str] = []
        self.successful_responses: List[Dict[str, Any]] = []
        self.start_time: float = 0
        self.end_time: float = 0
    
    def add_result(self, response_time: float, status_code: int, response_data: Dict[str, Any] = None, error: str = None):
        """Add a single request result"""
        self.response_times.append(response_time)
        self.status_codes.append(status_code)
        
        if error:
            self.errors.append(error)
        elif response_data:
            self.successful_responses.append(response_data)
    
    def print_summary(self):
        """Print comprehensive test results"""
        total_requests = len(self.response_times)
        successful_requests = len(self.successful_responses)
        failed_requests = len(self.errors)
        
        print("\n" + "="*60)
        print("🚀 LOAD TEST RESULTS")
        print("="*60)
        
        # Basic stats
        print(f"📊 Total Requests: {total_requests}")
        print(f"✅ Successful: {successful_requests} ({successful_requests/total_requests*100:.1f}%)")
        print(f"❌ Failed: {failed_requests} ({failed_requests/total_requests*100:.1f}%)")
        print(f"⏱️  Total Duration: {self.end_time - self.start_time:.2f}s")
        print(f"🔥 Requests/sec: {total_requests/(self.end_time - self.start_time):.2f}")
        
        if self.response_times:
            # Response time statistics
            print(f"\n📈 Response Time Statistics:")
            print(f"   Average: {statistics.mean(self.response_times):.3f}s")
            print(f"   Median:  {statistics.median(self.response_times):.3f}s")
            print(f"   Min:     {min(self.response_times):.3f}s")
            print(f"   Max:     {max(self.response_times):.3f}s")
            
            if len(self.response_times) > 1:
                print(f"   Std Dev: {statistics.stdev(self.response_times):.3f}s")
            
            # Percentiles
            sorted_times = sorted(self.response_times)
            p95_idx = int(0.95 * len(sorted_times))
            p99_idx = int(0.99 * len(sorted_times))
            print(f"   95th %:  {sorted_times[p95_idx]:.3f}s")
            print(f"   99th %:  {sorted_times[p99_idx]:.3f}s")
        
        # Status code breakdown
        if self.status_codes:
            status_counts = {}
            for code in self.status_codes:
                status_counts[code] = status_counts.get(code, 0) + 1
            
            print(f"\n📋 Status Code Breakdown:")
            for code, count in sorted(status_counts.items()):
                print(f"   {code}: {count} requests")
        
        # API response analysis
        if self.successful_responses:
            processing_times = [r.get('processing_time_ms', 0) for r in self.successful_responses if 'processing_time_ms' in r]
            extracted_texts = [r.get('extracted_text', '') for r in self.successful_responses if 'extracted_text' in r]
            
            if processing_times:
                print(f"\n🔬 API Processing Time (ms):")
                print(f"   Average: {statistics.mean(processing_times):.2f}ms")
                print(f"   Median:  {statistics.median(processing_times):.2f}ms")
                print(f"   Min:     {min(processing_times):.2f}ms")
                print(f"   Max:     {max(processing_times):.2f}ms")
            
            if extracted_texts:
                unique_texts = set(extracted_texts)
                print(f"\n🔤 Extracted Text Results:")
                print(f"   Unique results: {len(unique_texts)}")
                for text in sorted(unique_texts):
                    count = extracted_texts.count(text)
                    print(f"   '{text}': {count} times")
        
        # Errors
        if self.errors:
            print(f"\n❌ Error Summary:")
            error_counts = {}
            for error in self.errors:
                error_counts[error] = error_counts.get(error, 0) + 1
            
            for error, count in sorted(error_counts.items()):
                print(f"   {error}: {count} times")
        
        print("="*60)

async def send_request(session: aiohttp.ClientSession, url: str, image_path: str, semaphore: asyncio.Semaphore) -> tuple:
    """Send a single request to the API"""
    async with semaphore:
        start_time = time.time()
        
        try:
            # Read the image file
            with open(image_path, 'rb') as f:
                image_data = f.read()
            
            # Create form data
            data = aiohttp.FormData()
            data.add_field('file', image_data, filename='image.png', content_type='image/png')
            
            # Send request
            async with session.post(url, data=data) as response:
                response_time = time.time() - start_time
                
                if response.status == 200:
                    response_data = await response.json()
                    return response_time, response.status, response_data, None
                else:
                    error_text = await response.text()
                    return response_time, response.status, None, f"HTTP {response.status}: {error_text[:100]}"
                    
        except Exception as e:
            response_time = time.time() - start_time
            return response_time, 0, None, f"Exception: {str(e)[:100]}"

async def run_load_test(url: str, total_requests: int, concurrency: int, image_path: str) -> LoadTestResults:
    """Run the load test with specified parameters"""
    
    # Validate image file exists
    if not Path(image_path).exists():
        raise FileNotFoundError(f"Image file not found: {image_path}")
    
    print(f"🚀 Starting load test...")
    print(f"   URL: {url}")
    print(f"   Total requests: {total_requests}")
    print(f"   Concurrency: {concurrency}")
    print(f"   Image file: {image_path}")
    print(f"   Image size: {Path(image_path).stat().st_size} bytes")
    
    results = LoadTestResults()
    results.start_time = time.time()
    
    # Create semaphore to limit concurrency
    semaphore = asyncio.Semaphore(concurrency)
    
    # Configure session with reasonable timeouts
    timeout = aiohttp.ClientTimeout(total=30, connect=10)
    connector = aiohttp.TCPConnector(limit=concurrency * 2)
    
    async with aiohttp.ClientSession(timeout=timeout, connector=connector) as session:
        # Create all tasks
        tasks = [
            send_request(session, url, image_path, semaphore)
            for _ in range(total_requests)
        ]
        
        # Execute tasks and collect results
        print(f"\n⏳ Sending {total_requests} requests...")
        
        completed = 0
        for coro in asyncio.as_completed(tasks):
            response_time, status_code, response_data, error = await coro
            results.add_result(response_time, status_code, response_data, error)
            
            completed += 1
            if completed % 100 == 0 or completed == total_requests:
                print(f"   Progress: {completed}/{total_requests} ({completed/total_requests*100:.1f}%)")
    
    results.end_time = time.time()
    return results

def main():
    """Main function with CLI argument parsing"""
    parser = argparse.ArgumentParser(description="Load test the Shop Titans Text Classification API")
    parser.add_argument("--url", default=DEFAULT_URL, help=f"API endpoint URL (default: {DEFAULT_URL})")
    parser.add_argument("--requests", type=int, default=DEFAULT_TOTAL_REQUESTS, help=f"Total number of requests (default: {DEFAULT_TOTAL_REQUESTS})")
    parser.add_argument("--concurrency", type=int, default=DEFAULT_CONCURRENCY, help=f"Number of concurrent requests (default: {DEFAULT_CONCURRENCY})")
    parser.add_argument("--image", default=DEFAULT_IMAGE_PATH, help=f"Path to test image (default: {DEFAULT_IMAGE_PATH})")
    parser.add_argument("--output", help="Save results to JSON file")
    
    args = parser.parse_args()
    
    try:
        # Run the load test
        results = asyncio.run(run_load_test(args.url, args.requests, args.concurrency, args.image))
        
        # Print results
        results.print_summary()
        
        # Save results to file if requested
        if args.output:
            output_data = {
                "config": {
                    "url": args.url,
                    "total_requests": args.requests,
                    "concurrency": args.concurrency,
                    "image_path": args.image
                },
                "results": {
                    "total_requests": len(results.response_times),
                    "successful_requests": len(results.successful_responses),
                    "failed_requests": len(results.errors),
                    "duration_seconds": results.end_time - results.start_time,
                    "requests_per_second": len(results.response_times) / (results.end_time - results.start_time),
                    "response_times": results.response_times,
                    "status_codes": results.status_codes,
                    "errors": results.errors,
                    "sample_responses": results.successful_responses[:10]  # First 10 responses
                }
            }
            
            with open(args.output, 'w') as f:
                json.dump(output_data, f, indent=2)
            print(f"\n💾 Results saved to: {args.output}")
    
    except KeyboardInterrupt:
        print("\n⚠️  Load test interrupted by user")
    except Exception as e:
        print(f"\n❌ Error running load test: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
