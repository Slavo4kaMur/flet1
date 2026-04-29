import subprocess
import os
import sys

os.environ['PYTHONIOENCODING'] = 'utf-8'
project_dir = r"C:\PythonProject1\PythonProjec\flet_oop"
flutter_dir = r"C:\Users\Hatson\flutter\3.41.4"

print("Building APK for arm64 only...")

proc = subprocess.Popen(
    [r"C:\Users\Hatson\AppData\Local\Python\pythoncore-3.14-64\Scripts\flet.exe", "build", "apk", "--target-platform", "android-arm64"],
    cwd=project_dir,
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    env=os.environ
)

proc.stdin.write(b"y\n")
proc.stdin.flush()

output = b""
while True:
    try:
        chunk = proc.stdout.read1(8192)
        if not chunk:
            break
        output += chunk
    except:
        break

proc.wait()

with open(os.path.join(project_dir, "build_arm64_result.txt"), "wb") as f:
    f.write(output)

print("Done. Return code:", proc.returncode)