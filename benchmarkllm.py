import requests
import time
import statistics
import csv
from concurrent.futures import ThreadPoolExecutor, as_completed
import json

URL = "http://localhost:11434/api/chat"

MODELS_PARALLEL = ["llama3", "mistral"]
MODELS_SOLO = ["llama4"]  # large model, run solo

PROMPT = "Write a short paragraph about artificial intelligence."
NUM_REQUESTS = 5            # number of requests per model
CONCURRENCY_PER_MODEL = 2   # threads per model


def run_request(model, timeout=180):
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": PROMPT}],
        "stream": True
    }

    start = time.time()
    first_token_time = None
    final_answer = ""

    try:
        with requests.post(URL, json=payload, stream=True, timeout=timeout) as r:
            r.raise_for_status()
            current_content = ""

            for line in r.iter_lines():
                if line:
                    now = time.time()
                    if first_token_time is None:
                        first_token_time = now

                    try:
                        data = json.loads(line)
                        msg = data.get("message", {})
                        content_chunk = msg.get("content", "")
                        current_content += content_chunk

                        # Only return when done=True
                        if data.get("done", False):
                            final_answer = current_content
                            break
                    except json.JSONDecodeError:
                        continue

        end = time.time()
        tokens = len(final_answer.split())
        tps = tokens / (end - first_token_time) if first_token_time and tokens > 0 else 0

        return {
            "ttft": first_token_time - start if first_token_time else None,
            "latency": end - start,
            "tokens": tokens,
            "tps": round(tps, 2),
            "answer": final_answer
        }

    except Exception as e:
        return {"error": str(e)}


def percentile(data, p):
    if not data:
        return 0
    k = int(len(data) * p / 100)
    return sorted(data)[k]


def benchmark_model(model, timeout=180):
    results = []
    start_all = time.time()

    with ThreadPoolExecutor(max_workers=CONCURRENCY_PER_MODEL) as executor:
        futures = [executor.submit(run_request, model, timeout) for _ in range(NUM_REQUESTS)]
        for f in as_completed(futures):
            res = f.result()
            if "error" not in res:
                results.append(res)
            else:
                print(f"Error ({model}):", res["error"])

    end_all = time.time()

    if not results:
        return None

    ttfts = [r["ttft"] for r in results if r["ttft"]]
    latencies = [r["latency"] for r in results]
    tps_list = [r["tps"] for r in results if r["tps"] > 0]

    total_time = end_all - start_all
    throughput = len(results) / total_time if total_time > 0 else 0

    # Return metrics and final answer from the last request
    return {
        "model": model,
        "ttft_avg": round(statistics.mean(ttfts), 3) if ttfts else 0,
        "ttft_p50": round(percentile(ttfts, 50), 3),
        "ttft_p95": round(percentile(ttfts, 95), 3),
        "lat_avg": round(statistics.mean(latencies), 3),
        "lat_p50": round(percentile(latencies, 50), 3),
        "lat_p95": round(percentile(latencies, 95), 3),
        "tps_avg": round(statistics.mean(tps_list), 2) if tps_list else 0,
        "total_time": round(total_time, 2),
        "throughput": round(throughput, 2),
        "sample_answer": results[-1]["answer"] if results else ""
    }


def main():
    all_results = []

    print("=== Running parallel models ===")
    # Parallel small models
    with ThreadPoolExecutor(max_workers=len(MODELS_PARALLEL)) as executor:
        futures = {executor.submit(benchmark_model, m): m for m in MODELS_PARALLEL}
        for f in as_completed(futures):
            res = f.result()
            if res:
                all_results.append(res)

    print("\n=== Running solo large models ===")
    #for model in MODELS_SOLO:
    #    res = benchmark_model(model, timeout=600)
    #    if res:
    #        all_results.append(res)

    # Print table
    headers = ["model", "ttft_avg", "ttft_p50", "ttft_p95",
               "lat_avg", "lat_p50", "lat_p95", "tps_avg",
               "total_time", "throughput", "sample_answer"]

    print("\nMODEL      | TTFT(avg) | TTFT(p50) | TTFT(p95) | LAT(avg) | TPS(avg) | Total Time | Throughput")
    print("-" * 110)
    for r in all_results:
        print(f"{r['model']:10} | {r['ttft_avg']:9} | {r['ttft_p50']:9} | {r['ttft_p95']:9} | "
              f"{r['lat_avg']:8} | {r['tps_avg']:8} | {r['total_time']:10} | {r['throughput']:10}")
        # Print only final assistant answer
        print(f"Sample answer:\n{r['sample_answer'][:500]}...\n")  # truncate to 500 chars

    # Write CSV
    with open("benchmark_results.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(all_results)

    print("\nSaved results to benchmark_results.csv")


if __name__ == "__main__":
    main()
