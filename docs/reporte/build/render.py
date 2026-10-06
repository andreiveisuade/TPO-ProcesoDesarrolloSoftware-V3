import os, subprocess
out = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "puml")
r = subprocess.run("plantuml -tsvg -nometadata *.puml", shell=True, cwd=out, capture_output=True, text=True)
print(r.stdout, r.stderr)
