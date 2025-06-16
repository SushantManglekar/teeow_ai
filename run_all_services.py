import subprocess

services = [
    "api_gateway",
    "user_management_service",
    "chat_service",
    "affiliate_service",
    "ai_assistant_service",
    "trip_management_service",
    "subscription_service"
]

processes = []

for service in services:
    port = 8000 + services.index(service)
    cmd = [
        "uvicorn",
        f"{service}.main:app",
        "--reload",
        "--host", "0.0.0.0",
        "--port", str(port)
    ]
    print(f"Starting {service} on port {port}...")
    p = subprocess.Popen(cmd)
    processes.append(p)

# Wait for all processes indefinitely
for p in processes:
    p.wait()