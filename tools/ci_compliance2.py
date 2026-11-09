import io

p = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\.github\workflows\build-ios-signed.yml"
t = io.open(p, encoding="utf-8").read()

start = t.find("    - name: Declare export compliance in the exported plist")
assert start > 0
end = t.find("    - name: Write App Store export options")
assert end > start

step = '''    # Apple parks any build without this key in "Missing Compliance" and never hands it to
    # testers, which is why uploaded builds looked like they vanished.
    - name: Declare export compliance in the exported plists
      run: |
        set -e
        found=0
        while IFS= read -r plist; do
          /usr/libexec/PlistBuddy -c "Add :ITSAppUsesNonExemptEncryption bool false" "$plist" 2>/dev/null \\
            || /usr/libexec/PlistBuddy -c "Set :ITSAppUsesNonExemptEncryption false" "$plist"
          echo "patched $plist"
          /usr/libexec/PlistBuddy -c "Print :CFBundleVersion" "$plist"
          found=$((found+1))
        done < <(find build/ios -name Info.plist -not -path "*/export/*")
        test "$found" -gt 0

'''
t = t[:start] + step + t[end:]
io.open(p, "w", encoding="utf-8", newline="\n").write(t)
print("compliance step rewritten to patch every exported Info.plist")
