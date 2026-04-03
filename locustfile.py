from locust import HttpUser, task, between
import random
import logging

# --- config ---
MODELS = ["mistral", "llama3"]
WEIGHTS = [50, 50]  # must add to 100
PROMPT = "Explain AI in simple terms"
MAX_TOKENS = 100
WAIT_MIN = 1
WAIT_MAX = 3

class LLMUser(HttpUser):
    wait_time = between(WAIT_MIN, WAIT_MAX)

    @task
    def chat_completion(self):
        model = random.choices(MODELS, weights=WEIGHTS, k=1)[0]
        with self.client.post(
            "/v1/chat/completions",
            name=f"/v1/chat/completions [{model}]",
            json={
                "model": model,
                "messages": [{"role": "user", "content": PROMPT}],
                "max_tokens": MAX_TOKENS
            },
            headers={"Content-Type": "application/json"},
            catch_response=True  # lets you manually mark success/failure
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(
                    f"[{model}] status={response.status_code} body={response.text[:200]}"
                )
                logging.error(
                    f"[{model}] failed: status={response.status_code} body={response.text[:200]}"
                )
