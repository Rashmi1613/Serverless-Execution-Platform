import subprocess

# Map of language → container name
WARM_CONTAINERS = {
    "python": "warm-python-fn"
}

# Map of language → Docker image
CONTAINER_IMAGES = {
    "python": "my-python-image"
}

def start_warm_containers():
    for lang, container_name in WARM_CONTAINERS.items():
        image = CONTAINER_IMAGES.get(lang)
        if not image:
            continue

        # Check if already running
        status = subprocess.run(["docker", "ps", "-q", "-f", f"name={container_name}"], capture_output=True, text=True)
        if status.stdout.strip():
            print(f"[INFO] Warm container for {lang} already running.")
            continue

        # Start container
        print(f"[INFO] Starting warm container: {container_name}")
        cmd = [
            "docker", "run", "-d",
            "--name", container_name,
            image,
            "tail", "-f", "/dev/null"
        ]
        subprocess.run(cmd)
