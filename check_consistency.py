#!/usr/bin/env python3
"""
Consistency checker for ARC-AGI-2 Abstraction Dataset.

This script verifies that:
1. All solution files have corresponding abstraction files
2. All abstraction files have corresponding solution files
3. File counts match between solutions and abstractions
4. Task IDs are consistent across directories
5. Documentation reflects actual file counts

Usage:
    python check_consistency.py [--verbose]
"""

import os
import sys
import argparse
from pathlib import Path
from typing import Set, List, Tuple


def get_task_ids_from_solutions(solutions_dir: Path) -> Set[str]:
    """Extract task IDs from solution files."""
    task_ids = set()
    for file_path in solutions_dir.glob("*.py"):
        task_id = file_path.stem
        task_ids.add(task_id)
    return task_ids


def get_identity_stub_task_ids(solutions_dir: Path) -> Set[str]:
    """Extract task IDs that are identity function stubs (no abstractions expected)."""
    identity_task_ids = set()
    for file_path in solutions_dir.glob("*.py"):
        with open(file_path, 'r') as f:
            content = f.read()
            # Check if it's actually an identity stub by looking for the identity implementation
            # True identity stubs just return [row[:] for row in grid]
            if 'return [row[:] for row in grid]' in content and content.count('\n') < 15:
                task_id = file_path.stem
                identity_task_ids.add(task_id)
    return identity_task_ids


def get_task_ids_from_abstractions(abstractions_dir: Path) -> Set[str]:
    """Extract task IDs from abstraction files."""
    task_ids = set()
    for file_path in abstractions_dir.glob("task*_abstractions.py"):
        # Extract task ID from filename like "task135a2760_abstractions.py"
        task_id = file_path.stem.replace("task", "").replace("_abstractions", "")
        task_ids.add(task_id)
    return task_ids


def check_file_counts(solutions_dir: Path, abstractions_dir: Path) -> Tuple[int, int, int, int]:
    """Check file counts in each directory."""
    solution_count = len(list(solutions_dir.glob("*.py")))
    abstraction_py_count = len(list(abstractions_dir.glob("task*_abstractions.py")))
    abstraction_md_count = len(list(abstractions_dir.glob("task*_abstractions_report.md")))
    total_abstraction_count = len(list(abstractions_dir.glob("task*")))
    
    return solution_count, abstraction_py_count, abstraction_md_count, total_abstraction_count


def check_consistency(solutions_dir: Path, abstractions_dir: Path, verbose: bool = False) -> bool:
    """Check consistency between solutions and abstractions directories."""
    
    print("🔍 Checking ARC-AGI-2 Abstraction Dataset consistency...\n")
    
    # Get task IDs from both directories
    solution_task_ids = get_task_ids_from_solutions(solutions_dir)
    abstraction_task_ids = get_task_ids_from_abstractions(abstractions_dir)
    identity_stub_ids = get_identity_stub_task_ids(solutions_dir)
    
    # Check file counts
    solution_count, abstraction_py_count, abstraction_md_count, total_abstraction_count = check_file_counts(
        solutions_dir, abstractions_dir
    )
    
    print(f"📊 File Counts:")
    print(f"   Solutions: {solution_count}")
    if identity_stub_ids:
        print(f"   Identity stubs (no abstractions): {len(identity_stub_ids)}")
    print(f"   Abstraction Python files: {abstraction_py_count}")
    print(f"   Abstraction Markdown reports: {abstraction_md_count}")
    print(f"   Total abstraction files: {total_abstraction_count}")
    print()
    
    # Check for missing solutions (abstractions without solutions)
    missing_solutions = abstraction_task_ids - solution_task_ids
    if missing_solutions:
        print(f"❌ Missing solution files for {len(missing_solutions)} tasks:")
        for task_id in sorted(missing_solutions):
            print(f"   - {task_id}.py")
        print()
    
    # Check for missing abstractions (solutions without abstractions, excluding identity stubs)
    expected_abstractions = solution_task_ids - identity_stub_ids
    missing_abstractions = expected_abstractions - abstraction_task_ids
    if missing_abstractions:
        print(f"❌ Missing abstraction files for {len(missing_abstractions)} tasks:")
        for task_id in sorted(missing_abstractions):
            print(f"   - task{task_id}_abstractions.py")
            print(f"   - task{task_id}_abstractions_report.md")
        print()
    
    # Check for individual missing files
    missing_files = []
    for task_id in solution_task_ids & abstraction_task_ids:
        abstraction_py = abstractions_dir / f"task{task_id}_abstractions.py"
        abstraction_md = abstractions_dir / f"task{task_id}_abstractions_report.md"
        
        if not abstraction_py.exists():
            missing_files.append(f"task{task_id}_abstractions.py")
        if not abstraction_md.exists():
            missing_files.append(f"task{task_id}_abstractions_report.md")
    
    if missing_files:
        print(f"❌ Missing individual abstraction files ({len(missing_files)} files):")
        for file in sorted(missing_files):
            print(f"   - {file}")
        print()
    
    # Check if counts match (accounting for identity stubs)
    count_issues = []
    expected_abstraction_count = solution_count - len(identity_stub_ids)
    if expected_abstraction_count != abstraction_py_count:
        count_issues.append(f"Expected abstraction count ({expected_abstraction_count}) != Actual abstraction Python count ({abstraction_py_count})")
    if abstraction_py_count != abstraction_md_count:
        count_issues.append(f"Abstraction Python count ({abstraction_py_count}) != Abstraction Markdown count ({abstraction_md_count})")
    if total_abstraction_count != abstraction_py_count + abstraction_md_count:
        count_issues.append(f"Total abstraction count ({total_abstraction_count}) != Python + Markdown count ({abstraction_py_count + abstraction_md_count})")
    
    if count_issues:
        print(f"❌ Count mismatches:")
        for issue in count_issues:
            print(f"   - {issue}")
        print()
    
    # Summary
    total_issues = len(missing_solutions) + len(missing_abstractions) + len(missing_files) + len(count_issues)
    
    if total_issues == 0:
        print("✅ All consistency checks passed!")
        print(f"   Dataset contains {solution_count} total solutions")
        print(f"   - {abstraction_py_count} with full abstraction analysis")
        if identity_stub_ids:
            print(f"   - {len(identity_stub_ids)} identity stubs (baseline)")
        return True
    else:
        print(f"❌ Found {total_issues} consistency issues")
        return False


def check_documentation_consistency(verbose: bool = False) -> bool:
    """Check if documentation reflects actual file counts and has no placeholders."""
    print("📚 Checking documentation consistency...\n")
    
    issues_found = 0
    
    # Read README.md
    readme_path = Path("README.md")
    if not readme_path.exists():
        print("❌ README.md not found")
        return False
    
    with open(readme_path, 'r') as f:
        readme_content = f.read()
    
    # Count tasks mentioned in README
    import re
    readme_task_counts = re.findall(r'\b(\d+)\s+tasks?\b', readme_content)
    if verbose:
        print(f"Task counts found in README: {readme_task_counts}")
    
    # Get actual counts
    solutions_dir = Path("solutions")
    abstractions_dir = Path("abstractions")
    
    if not solutions_dir.exists() or not abstractions_dir.exists():
        print("❌ solutions/ or abstractions/ directories not found")
        return False
    
    actual_count = len(list(solutions_dir.glob("*.py")))
    
    # Check if README mentions the correct count
    if str(actual_count) not in readme_content:
        print(f"❌ README.md doesn't mention current task count ({actual_count})")
        print(f"   Found mentions of: {readme_task_counts}")
        issues_found += 1
    else:
        print(f"✅ README.md correctly mentions {actual_count} tasks")
    
    # Check CHANGELOG.md for placeholder dates
    changelog_path = Path("CHANGELOG.md")
    if changelog_path.exists():
        with open(changelog_path, 'r') as f:
            changelog_content = f.read()
        
        # Look for placeholder dates like "2025-01-XX" or "YYYY-MM-XX"
        placeholder_dates = re.findall(r'\d{4}-\d{2}-XX', changelog_content)
        if placeholder_dates:
            print(f"❌ CHANGELOG.md contains placeholder dates: {placeholder_dates}")
            issues_found += 1
        else:
            print("✅ CHANGELOG.md has no placeholder dates")
        
        # Check for TODO or FIXME comments
        todo_comments = re.findall(r'(TODO|FIXME|XXX)', changelog_content, re.IGNORECASE)
        if todo_comments:
            print(f"⚠️  CHANGELOG.md contains TODO/FIXME comments: {set(todo_comments)}")
    
    # Check for other common placeholder patterns
    placeholder_patterns = [
        r'<[A-Z_]+>',  # <PLACEHOLDER>
        r'\[TODO\]',   # [TODO]
        r'XXX',        # XXX
        r'PLACEHOLDER' # PLACEHOLDER
    ]
    
    for pattern in placeholder_patterns:
        matches = re.findall(pattern, readme_content, re.IGNORECASE)
        if matches:
            print(f"⚠️  README.md contains potential placeholders ({pattern}): {set(matches)}")
    
    return issues_found == 0


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Check ARC-AGI-2 dataset consistency")
    parser.add_argument("--verbose", "-v", action="store_true", 
                       help="Enable verbose output")
    args = parser.parse_args()
    
    # Check if we're in the right directory
    if not Path("solutions").exists() or not Path("abstractions").exists():
        print("❌ Error: Must run from repository root directory")
        print("   Expected to find 'solutions/' and 'abstractions/' directories")
        sys.exit(1)
    
    solutions_dir = Path("solutions")
    abstractions_dir = Path("abstractions")
    
    # Run consistency checks
    consistency_ok = check_consistency(solutions_dir, abstractions_dir, args.verbose)
    doc_ok = check_documentation_consistency(args.verbose)
    
    print("\n" + "="*50)
    if consistency_ok and doc_ok:
        print("🎉 All checks passed! Repository is consistent.")
        sys.exit(0)
    else:
        print("💥 Some checks failed. Please fix the issues above.")
        sys.exit(1)


if __name__ == "__main__":
    main()
