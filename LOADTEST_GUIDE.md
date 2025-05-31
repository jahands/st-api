# Load Testing Guide

This guide explains how to use the load testing script to test the performance of your Shop Titans Text Classification API.

## 🚀 Quick Start

### Run Default Load Test
```bash
just loadtest
```
This sends 1000 requests with 10x concurrency to `https://st-api.geostyx.com/classify`

### Available Load Test Commands

| Command | Requests | Concurrency | Description |
|---------|----------|-------------|-------------|
| `just loadtest` | 1000 | 10 | Default production load test |
| `just loadtest-quick` | 100 | 5 | Quick test for validation |
| `just loadtest-intensive` | 5000 | 20 | Intensive stress test |
| `just loadtest-local` | 100 | 5 | Test local Railway container |

### Custom Load Test
```bash
just loadtest-custom "https://your-api.com/classify" 2000 15
```

## 📊 Understanding Results

### Key Metrics

- **Requests/sec**: Throughput of your API
- **Response Time**: End-to-end latency including network
- **API Processing Time**: Server-side processing time only
- **Success Rate**: Percentage of successful requests
- **95th/99th Percentile**: Response times for slowest requests

### Sample Output
```
============================================================
🚀 LOAD TEST RESULTS
============================================================
📊 Total Requests: 1000
✅ Successful: 999 (99.9%)
❌ Failed: 1 (0.1%)
⏱️  Total Duration: 45.46s
🔥 Requests/sec: 22.00

📈 Response Time Statistics:
   Average: 0.453s
   Median:  0.442s
   Min:     0.137s
   Max:     1.076s
   95th %:  0.596s
   99th %:  0.847s

🔬 API Processing Time (ms):
   Average: 44.40ms
   Median:  42.00ms
   Min:     36.15ms
   Max:     71.53ms
```

## 🔧 Advanced Usage

### Direct Script Usage
```bash
# Basic usage
uv run python scripts/loadtest.py --url "https://st-api.geostyx.com/classify"

# Custom parameters
uv run python scripts/loadtest.py \
  --url "https://your-api.com/classify" \
  --requests 2000 \
  --concurrency 20 \
  --image "path/to/your/image.png" \
  --output "results.json"
```

### Command Line Options

| Option | Default | Description |
|--------|---------|-------------|
| `--url` | `https://st-api.geostyx.com/classify` | API endpoint URL |
| `--requests` | 1000 | Total number of requests |
| `--concurrency` | 10 | Number of concurrent requests |
| `--image` | `data/image.png` | Path to test image |
| `--output` | None | Save results to JSON file |

### Save Results to File
```bash
uv run python scripts/loadtest.py --output loadtest_results.json
```

## 📈 Performance Benchmarks

### Expected Performance (Railway Deployment)

- **Throughput**: 20-25 requests/sec
- **Response Time**: 400-500ms average
- **API Processing**: 40-50ms average
- **Success Rate**: >99%

### Factors Affecting Performance

1. **Network Latency**: Distance to Railway servers
2. **Image Size**: Larger images take longer to process
3. **Concurrency**: Higher concurrency may increase response times
4. **Cold Starts**: First requests may be slower

## 🛠️ Troubleshooting

### Common Issues

1. **High Error Rate**
   - Check API health: `curl https://st-api.geostyx.com/health`
   - Reduce concurrency if getting 502/503 errors
   - Verify image file exists and is readable

2. **Slow Response Times**
   - Check network connectivity
   - Try reducing concurrency
   - Monitor Railway logs: `just railway-logs`

3. **Connection Errors**
   - Verify URL is correct
   - Check if API is deployed and running
   - Test with single request first

### Debug Single Request
```bash
curl -X POST "https://st-api.geostyx.com/classify" \
     -F "file=@data/image.png" \
     -w "Time: %{time_total}s\n"
```

## 📊 Interpreting Results

### Good Performance Indicators
- ✅ Success rate > 99%
- ✅ 95th percentile < 1 second
- ✅ Consistent processing times
- ✅ No timeout errors

### Performance Issues
- ❌ Success rate < 95%
- ❌ High variance in response times
- ❌ Many 502/503 errors
- ❌ Timeouts or connection errors

### Optimization Tips

1. **For High Latency**: Consider CDN or edge deployment
2. **For Low Throughput**: Scale up Railway service
3. **For Errors**: Check Railway logs and resource limits
4. **For Inconsistency**: Monitor during different times of day

## 🔍 Monitoring Production

### Regular Health Checks
```bash
# Quick health check
curl https://st-api.geostyx.com/health

# Performance validation
just loadtest-quick
```

### Continuous Monitoring
- Set up automated load tests
- Monitor Railway metrics
- Track response times over time
- Alert on error rate increases
