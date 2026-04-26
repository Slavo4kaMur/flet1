import subprocess
import os
import sys
import time

os.environ['PYTHONIOENCODING'] = 'utf-8'
os.environ['ANDROID_HOME'] = r'C:\Users\HatsuneWin\Android\sdk'
os.environ['FLUTTER_ALLOWED_HTTP_DOMAINS'] = '*'

project_dir = r"C:\Users\HatsuneWin\Desktop\NikitaProgect\flet_oop-6"
flet = r"C:\Users\HatsuneWin\Desktop\NikitaProgect\flet_oop-6\.venv\Scripts\flet.exe"

print("Building APK...")

proc = subprocess.Popen(
    [flet, "build", "apk"],
    cwd=project_dir,
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    env=os.environ
)

for _ in range(10):
    time.sleep(2)
    proc.stdin.write(b"y\n")
    proc.stdin.flush()
    if proc.poll() is not None:
        break

output = b""
while proc.poll() is None:
    try:
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

with open(os.path.join(project_dir, "build_result.txt"), "w", encoding="utf-8", errors="ignore") as f:
    f.write(output.decode("utf-8", errors="ignore"))

print("Done. Return code:", proc.returncode)
if os.path.exists(os.path.join(project_dir, "build", "apk", "flet_oop.apk")):
    print("APK: build/apk/flet_oop.apk")
else:
    print("Check build_result.txt")