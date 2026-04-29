import subprocess
import os
import sys
import time

os.environ['PYTHONIOENCODING'] = 'utf-8'
os.environ['FLUTTER_ALLOWED_HTTP_DOMAINS'] = '*'

project_dir = r"C:\PythonProject1\PythonProjec\flet_oop"
flutter = r"C:\Users\Hatson\flutter\3.41.4\bin\flutter.bat"

print("Building APK...")

proc = subprocess.Popen(
    [sys.executable, r"C:\Users\Hatson\AppData\Local\Python\pythoncore-3.14-64\Scripts\flet.exe", "build", "apk"],
    cwd=project_dir,
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    env=os.environ
)

time.sleep(3)
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

with open(os.path.join(project_dir, "build_result.txt"), "wb") as f:
    f.write(output)

print("Done. Return code:", proc.returncode)
print("Check build_result.txt")
