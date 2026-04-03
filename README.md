
- Measures throughput
- Higher TPS = faster streaming output

---

## 3. Statistical Latency Metrics

### LAT_avg (Average Latency)
- Mean latency across all requests
- Sensitive to outliers

---

### LAT_p50 (Median Latency)
- 50th percentile
- Represents typical user experience
- More robust than average

---

### LAT_p95 (95th Percentile Latency)
- 95% of requests are faster than this value
- Highlights tail latency (slowest experiences)

---

### Why Percentiles Matter

Example:

| Metric   | System A | System B |
|----------|----------|----------|
| LAT_avg  | 2.0 s    | 2.0 s    |
| LAT_p50  | 1.5 s    | 1.0 s    |
| LAT_p95  | 2.2 s    | 5.0 s    |

- Same average
- Very different user experience
- System B has worse tail latency

---

## 4. Locust Metrics

Locust operates at the HTTP request level and provides the following:

### Request Metrics
- Total requests
- Failures
- Requests per second (RPS)

---

### Response Time Metrics
- Average response time → LAT_avg
- Median response time → LAT_p50
- Percentiles (p90, p95, p99) → LAT_p95, etc.
- Min / Max response time

---

### Distribution Metrics
- Response time histogram
- Helps visualize latency spread

---

### Reliability Metrics
- Failure count
- Error rate

---

## 5. What Locust Does NOT Provide

### TTFT
- Not measured by default
- Requires custom instrumentation

---

### TPS (Tokens Per Second)
- Not available natively
- Requires token counting and timing

---

### Token-Level Latency
- No built-in support
- Requires streaming-aware implementation

---

## 6. Extending Locust for LLM Metrics

### Measuring TTFT
- Use streaming APIs (SSE/WebSockets)
- Record:
  - Request start time
  - First token arrival time

---

### Measuring TPS
- Count tokens in response
- Measure generation duration
- Compute TPS manually

---

### Recommended Tracking
- TTFT (p50, p95)
- Full latency (p50, p95)
- TPS distribution

---

## 7. Summary Table

| Metric   | Description                     | Locust Support |
|----------|--------------------------------|----------------|
| TTFT     | Time to first token            | No (custom)    |
| LAT_avg  | Average full latency           | Yes            |
| LAT_p50  | Median latency                 | Yes            |
| LAT_p95  | Tail latency                   | Yes            |
| TPS      | Token generation speed         | No (custom)    |
| RPS      | Requests per second            | Yes            |

---

## 8. Key Takeaways

- TTFT determines responsiveness
- LAT determines total wait time
- TPS determines streaming speed
- Percentiles reveal consistency
- Locust is useful for system-level metrics but needs extensions for LLM-specific insights
