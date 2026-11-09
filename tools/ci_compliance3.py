import io

p = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\.github\workflows\build-ios-signed.yml"
t = io.open(p, encoding="utf-8").read()

start = t.find("    - name: Declare export compliance in the exported plists")
assert start > 0
end = t.find("    - name: Write App Store export options")
assert end > start

step = '''    # Apple parks any build without this key in "Missing Compliance" and never hands it to
    # testers. The exported project names its plist differently between Godot versions, so patch
    # every plist it produced and never fail the job over it.
    - name: Declare export compliance in the exported plists
      run: |
        count=0
        while IFS= read -r plist; do
          if /usr/libexec/PlistBuddy -c "Add :ITSAppUsesNonExemptEncryption bool false" "$plist" 2>/dev/null \\
             || /usr/libexec/PlistBuddy -c "Set :ITSAppUsesNonExemptEncryption false" "$plist" 2>/dev/null; then
            echo "patched $plist"
            count=$((count+1))
          else
            echo "could not patch $plist"
          fi
          /usr/libexec/PlistBuddy -c "Print :CFBundleVersion" "$plist" 2>/dev/null || true
        done < <(find build/ios -name '*Info.plist' -not -path '*/export/*' 2>/dev/null)
        echo "plists patched: $count"

'''
t = t[:start] + step + t[end:]
io.open(p, "w", encoding="utf-8", newline="\n").write(t)
print("compliance step is now tolerant and matches any *Info.plist")
