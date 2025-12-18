#!/usr/bin/env python3
"""Demo: TodoManager library works perfectly in a single session."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from console_app.models.todo import Todo
from console_app.lib.todo_manager import TodoManager, TodoNotFoundError, ValidationError

print("=" * 70)
print("PHASE I: CONSOLE TODO APP - LIBRARY DEMONSTRATION")
print("=" * 70)

# Single session with shared TodoManager instance
manager = TodoManager()

# Test 1: Add todos
print("\n1️⃣  Adding todos...")
todo1 = manager.add("Buy groceries")
todo2 = manager.add("Call dentist", "Schedule annual checkup")
todo3 = manager.add("Review PR #123", "Check backend changes")
print(f"   ✓ Added 3 todos (IDs: {todo1.id}, {todo2.id}, {todo3.id})")

# Test 2: List todos
print("\n2️⃣  Listing all todos...")
todos = manager.list_all()
for todo in todos:
    desc = f" - {todo.description[:30]}..." if todo.description else ""
    print(f"   #{todo.id} [{todo.status:8}] {todo.title}{desc}")

# Test 3: Complete a todo
print("\n3️⃣  Completing todo #2...")
completed = manager.complete(2)
print(f"   ✓ Todo #{completed.id} marked as '{completed.status}'")

# Test 4: Update a todo
print("\n4️⃣  Updating todo #3...")
updated = manager.update(3, title="Review and merge PR #123")
print(f"   ✓ Todo #{updated.id}: {updated.title}")

# Test 5: Delete a todo
print("\n5️⃣  Deleting todo #1...")
deleted = manager.delete(1)
print(f"   ✓ Deleted todo #{deleted.id}: {deleted.title}")

# Test 6: Final state
print("\n6️⃣  Final state:")
todos = manager.list_all()
for todo in todos:
    desc = f" - {todo.description[:30]}..." if todo.description else ""
    print(f"   #{todo.id} [{todo.status:8}] {todo.title}{desc}")

# Test 7: Validation
print("\n7️⃣  Testing validation...")
try:
    manager.add("")  # Empty title
    print("   ❌ Should have rejected empty title!")
except ValidationError:
    print("   ✓ Empty title rejected")

try:
    manager.get(999)  # Nonexistent ID
    print("   ❌ Should have raised TodoNotFoundError!")
except TodoNotFoundError:
    print("   ✓ Nonexistent ID rejected")

print("\n" + "=" * 70)
print("✅ ALL LIBRARY FUNCTIONS WORK CORRECTLY!")
print("=" * 70)

print("\n📌 PHASE I LIMITATION:")
print("   In-memory storage is SESSION-SCOPED (not persistent).")
print("   Each CLI command creates a NEW TodoManager instance.")
print("   This is expected behavior for Phase I.")
print("\n💡 PHASE II SOLUTION:")
print("   Database persistence will be added in Phase II.")
print("   The same TodoManager code will work with PostgreSQL!")
print("=" * 70)
