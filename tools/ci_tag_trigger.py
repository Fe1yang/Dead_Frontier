import io

p = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\.github\workflows\build-ios-signed.yml"
t = io.open(p, encoding="utf-8").read()

old = '''  # push:
  #   branches: [main]   # deliberately off: builds are dispatched manually
'''
new = '''  # Branch pushes stay off (builds would fire on every commit), but a build tag is a deliberate
  # one-line trigger:  git tag build-18 && git push origin build-18
  push:
    tags:
      - "build-*"
'''

assert t.count(old) == 1, t.count(old)
t = t.replace(old, new, 1)
io.open(p, "w", encoding="utf-8", newline="\n").write(t)
print("workflow now triggers on build-* tags")
