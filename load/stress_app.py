import time
import requests
import random

# Target the backend service within the docker network
BASE_URL = "http://backend:4000/api"

def generate_load():
    endpoints = [
        ('/posts', 'GET'),
        # ('/posts', 'POST'), # Skip POST to avoid flooding DB with garbage for now, or implement login first
        # We can try to hit the public endpoints first
    ]
    
    print(f"Starting load generation against {BASE_URL}...")
    
    while True:
        try:
            # Simple GET request to list posts
            response = requests.get(f"{BASE_URL}/posts")
            print(f"GET /posts: {response.status_code}")
            
            # Simulate some think time
            time.sleep(random.uniform(0.5, 2.0))
            
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(5)

if __name__ == "__main__":
    # Wait for backend to be ready
    time.sleep(10)
    generate_load()
