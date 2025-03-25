import subprocess
import sys

def start_celery_worker():
    try:
        command = [
            "celery", "-A", "celery_service.celery_config",
            "worker", "-l", "info", "-P", "threads"
        ]
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error starting Celery worker: {e}")

def stop_celery_worker():
    try:
        command = ["pkill", "-f", "celery"]
        subprocess.run(command, check=True)
        print("Celery worker stopped successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error stopping Celery worker: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "--run":
            start_celery_worker()
        elif sys.argv[1] == "--stop":
            stop_celery_worker()
        else:
            print("Invalid argument. Use --run to start or --stop to stop the worker.")
    else:
        print("Please provide an argument: --run or --stop")
        