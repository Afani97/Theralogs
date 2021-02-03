import subprocess

process = subprocess.Popen(
    ["python", "manage.py", "process_tasks"],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
)
