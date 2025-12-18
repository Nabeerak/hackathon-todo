#!/usr/bin/env python3
"""Demo script to test all CLI functionality."""

import subprocess
import sys
from pathlib import Path

CLI_PATH = Path(__file__).parent / "src" / "console_app" / "cli" / "main.py"
PYTHONPATH = Path(__file__).parent / "src"

def run_cli(*args):
    """Run CLI command and return result."""
    env = {"PYTHONPATH": str(PYTHONPATH)}
    result = subprocess.run(
        [sys.executable, str(CLI_PATH)] + list(args),
        capture_output=True,
        text=True,
        env=env
    )
    return result

print("=" * 60)
print("CONSOLE TODO APP - FUNCTIONALITY TEST")
print("=" * 60)

# Test 1: Add todos
print("\n1️⃣  Testing ADD command...")
result = run_cli("add", "Buy groceries")
print(f"   {result.stdout.strip()}")
assert result.returncode == 0

result = run_cli("add", "Call dentist", "--description", "Schedule annual checkup")
print(f"   {result.stdout.strip()}")
assert result.returncode == 0

result = run_cli("add", "Review PR #123", "-d", "Check backend changes")
print(f"   {result.stdout.strip()}")
assert result.returncode == 0

# Test 2: List todos
print("\n2️⃣  Testing LIST command...")
result = run_cli("list")
print(result.stdout)
assert result.returncode == 0
assert "Buy groceries" in result.stdout
assert "Call dentist" in result.stdout
assert "Review PR #123" in result.stdout

# Test 3: List alias
print("3️⃣  Testing LS alias...")
result = run_cli("ls")
assert result.returncode == 0
assert "Buy groceries" in result.stdout
print("   ✅ Alias works!")

# Test 4: Complete todo
print("\n4️⃣  Testing COMPLETE command...")
result = run_cli("complete", "2")
print(f"   {result.stdout.strip()}")
assert result.returncode == 0

# Verify status changed
result = run_cli("list")
print("\n   After completing todo #2:")
print(result.stdout)

# Test 5: Complete alias
print("5️⃣  Testing DONE alias...")
result = run_cli("done", "1")
print(f"   {result.stdout.strip()}")
assert result.returncode == 0
print("   ✅ Alias works!")

# Test 6: Update todo
print("\n6️⃣  Testing UPDATE command...")
result = run_cli("update", "3", "--title", "Review and merge PR #123")
print(f"   {result.stdout.strip()}")
assert result.returncode == 0

# Verify update
result = run_cli("list")
print("\n   After updating todo #3:")
print(result.stdout)

# Test 7: Delete todo
print("7️⃣  Testing DELETE command...")
result = run_cli("delete", "1")
print(f"   {result.stdout.strip()}")
assert result.returncode == 0

# Test 8: Delete alias
print("\n8️⃣  Testing RM alias...")
result = run_cli("rm", "2")
print(f"   {result.stdout.strip()}")
assert result.returncode == 0
print("   ✅ Alias works!")

# Final list
print("\n9️⃣  Final state:")
result = run_cli("list")
print(result.stdout)

# Test 10: Error handling
print("🔟 Testing ERROR handling...")
result = run_cli("add", "")
assert result.returncode == 1
print(f"   Empty title rejected: {result.stderr.strip()}")

result = run_cli("complete", "999")
assert result.returncode == 2
print(f"   Nonexistent ID rejected: {result.stderr.strip()}")

# Test 11: Help and version
print("\n1️⃣1️⃣  Testing HELP and VERSION...")
result = run_cli("--version")
print(f"   Version: {result.stdout.strip()}")
assert result.returncode == 0

result = run_cli("--help")
assert result.returncode == 0
assert "todo" in result.stdout.lower()
print("   ✅ Help works!")

print("\n" + "=" * 60)
print("✅ ALL TESTS PASSED!")
print("=" * 60)
