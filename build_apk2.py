import subprocess
import os
import sys

os.environ['PYTHONIOENCODING'] = 'utf-8'
os.environ['ANDROID_HOME'] = r'C:\Users\HatsuneWin\Android\sdk'

project_dir = r"C:\Users\HatsuneWin\Desktop\NikitaProgect\flet_oop-6"
flet_exe = r"C:\Users\HatsuneWin\Desktop\NikitaProgect\flet_oop-6\.venv\Scripts\flet.exe"

# Clean build dirs
for d in ["build", ".flet"]:
    path = os.path.join(project_dir, d)
    if os.path.exists(path):
        import shutil
        shutil.rmtree(path, ignore_errors=True)

print("Starting build...")

proc = subprocess.Popen(
    [flet_exe, "build", "apk"],
    cwd=project_dir,
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    env=os.environ
)

# Answer "y" to any prompts
for _ in range(15):
    import time
    time.sleep(2)
    if proc.poll() is not None:
        break
    try:
        proc.stdin.write(b"y\n")
        proc.stdin.flush()
    except:
        break

output = b""
while proc.poll() is None:
    try:
        import time
        chunk = proc.stdout.read1(8192)
        if chunk:
            output += chunk
        else:
            time.sleep(1)
    except:
        break

if proc.poll() is None:
    proc.terminate()

proc.wait()

with open(os.path.join(project_dir, "build_result2.txt"), "w", encoding="utf-8", errors="ignore") as f:
    f.write(output.decode("utf-8", errors="ignore"))

print("Done. Return code:", proc.returncode)
apk_path = os.path.join(project_dir, "build", "apk", "flet_oop.apk")
if os.path.exists(apk_path):
    print(f"APK: {apk_path}")
else:
    print("APK not found, check build_result2.txt")