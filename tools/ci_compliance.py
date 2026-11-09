import io

p = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\.github\workflows\build-ios-signed.yml"
t = io.open(p, encoding="utf-8").read()

if "ITSAppUsesNonExemptEncryption" in t:
    print("compliance key already handled")
else:
    anchor = "    - name: Write App Store export options\n"
    assert t.count(anchor) == 1, t.count(anchor)
    step = '''    # Apple parks any build without this key in "Missing Compliance" and never hands it to
    # testers, which is why uploaded builds looked like they vanished.
    - name: Declare export compliance in the exported plist
      run: |
        set -e
        PLIST="build/ios/${NAME}/Info.plist"
        test -f "$PLIST"
        /usr/libexec/PlistBuddy -c "Delete :ITSAppUsesNonExemptEncryption" "$PLIST" 2>/dev/null || true
        /usr/libexec/PlistBuddy -c "Add :ITSAppUsesNonExemptEncryption bool false" "$PLIST"
        /usr/libexec/PlistBuddy -c "Print :ITSAppUsesNonExemptEncryption" "$PLIST"
        /usr/libexec/PlistBuddy -c "Print :CFBundleVersion" "$PLIST"
        /usr/libexec/PlistBuddy -c "Print :CFBundleShortVersionString" "$PLIST"

'''
    t = t.replace(anchor, step + anchor, 1)
    io.open(p, "w", encoding="utf-8", newline="\n").write(t)
    print("compliance step inserted before the archive")
