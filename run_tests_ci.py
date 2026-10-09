"""
CI Test Runner for KM Layout Tables Studio.
Runs pytest in an isolated subprocess to protect CI from PySide6 C++ exit teardown crashes on Windows.
"""
import sys
import subprocess
import xml.etree.ElementTree as ET

def main():
    cmd = [sys.executable, "-m", "pytest", "--junitxml=test-results.xml"]
    print(f"Executing: {' '.join(cmd)}\n")
    subprocess.run(cmd)

    try:
        tree = ET.parse("test-results.xml")
        root = tree.getroot()
        suite = root.find("testsuite")
        if suite is None:
            suite = root
        tests = int(suite.attrib.get("tests", 0))
        failures = int(suite.attrib.get("failures", 0))
        errors = int(suite.attrib.get("errors", 0))
        print("\n==========================================")
        print(f"CI Summary: {tests} tests run | {failures} failures | {errors} errors")
        print("==========================================\n")
        if failures == 0 and errors == 0 and tests > 0:
            sys.exit(0)
        else:
            sys.exit(1)
    except Exception as err:
        print(f"Error reading test-results.xml: {err}")
        sys.exit(1)

if __name__ == "__main__":
    main()
