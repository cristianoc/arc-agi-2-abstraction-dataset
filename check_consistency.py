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
    
    # Check file counts
    solution_count, abstraction_py_count, abstraction_md_count, total_abstraction_count = check_file_counts(
        solutions_dir, abstractions_dir
    )
    
    print(f"📊 File Counts:")
    print(f"   Solutions: {solution_count}")
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
    
    # Check for missing abstractions (solutions without abstractions)
    missing_abstractions = solution_task_ids - abstraction_task_ids
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
    
    # Check if counts match
    count_issues = []
    if solution_count != abstraction_py_count:
        count_issues.append(f"Solution count ({solution_count}) != Abstraction Python count ({abstraction_py_count})")
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
        print(f"   Dataset contains {solution_count} complete task implementations")
        return True
    else:
        print(f"❌ Found {total_issues} consistency issues")
        return False


def check_documentation_consistency(verbose: bool = False) -> bool:
    """Check if documentation reflects actual file counts."""
    print("📚 Checking documentation consistency...\n")
    
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
        return False
    
    print(f"✅ README.md correctly mentions {actual_count} tasks")
    return True


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
