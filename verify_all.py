import subprocess
import time
import urllib.request
import urllib.error
import json
import sys

def run_tests():
    server_process = None
    try:
        # Start server
        print("Starting FastAPI server...")
        server_process = subprocess.Popen(
            [sys.executable, "run.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Wait for server to start
        print("Waiting for server to start...")
        max_retries = 10
        for i in range(max_retries):
            try:
                # GET /health
                req = urllib.request.urlopen("http://127.0.0.1:8000/health", timeout=2)
                if req.status == 200:
                    print("GET /health returned 200 OK")
                    break
            except Exception:
                time.sleep(1)
        else:
            raise RuntimeError("FastAPI server failed to start or /health did not return 200")

        # POST /chat
        print("Testing POST /chat...")
        payload = {
            "messages": [
                {
                    "role": "user",
                    "content": "Hiring a senior engineering manager needing leadership and personality evaluation"
                }
            ]
        }
        data = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(
            "http://127.0.0.1:8000/chat",
            data=data,
            headers={'Content-Type': 'application/json'}
        )
        
        try:
            with urllib.request.urlopen(req) as response:
                res_data = json.loads(response.read().decode())
                print("POST /chat response status:", response.status)
                print("POST /chat response reply:", res_data.get("reply"))
                if "recommendations" not in res_data:
                    raise RuntimeError("Response missing 'recommendations'")
                print("POST /chat works correctly!")
        except urllib.error.HTTPError as e:
            raise RuntimeError(f"POST /chat failed: {e.code} - {e.read().decode()}")
        
        # Run evaluation suite
        print("Running evaluation suite...")
        eval_res = subprocess.run(
            [sys.executable, "evaluation/eval.py"],
            capture_output=True,
            text=True
        )
        print("Evaluation suite stdout:")
        print(eval_res.stdout)
        if eval_res.stderr:
            print("Evaluation suite stderr:")
            print(eval_res.stderr)
            
        if eval_res.returncode != 0:
            raise RuntimeError(f"Evaluation suite exited with code {eval_res.returncode}")
        
        # Check if the evaluation output has failures or errors.
        if "[FAIL]" in eval_res.stdout or "[ERROR]" in eval_res.stdout:
            raise RuntimeError("Evaluation suite had probe or schema failures.")

        print("All verifications passed successfully!")
    
    finally:
        if server_process:
            print("Terminating server...")
            server_process.terminate()
            try:
                server_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                server_process.kill()
            print("Server terminated.")

if __name__ == "__main__":
    try:
        run_tests()
    except Exception as e:
        print(f"VERIFICATION FAILED: {e}", file=sys.stderr)
        sys.exit(1)
