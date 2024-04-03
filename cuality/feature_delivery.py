import subprocess
from datetime import datetime
import sys
from os import chdir
from pathlib import Path

import numpy as np


def run_git_command(cmd):
    """Runs a git command and returns its output."""
    result = subprocess.run(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, check=True
    )
    return result.stdout.decode("utf-8")


def get_merge_commits(
    branch_name: str = "main",
) -> dict[str, datetime]:
    cmd = f"git log --merges --pretty=format:'%H %cd' --date=iso {branch_name}"
    output = run_git_command(cmd)
    merges = [line.split(" ", maxsplit=1) for line in output.strip().split("\n")]
    return {commit: datetime.fromisoformat(date) for commit, date in merges}


def get_branch_points(
    merge_commits: dict[str, tuple[str, str, str]]
) -> dict[str, datetime]:
    branch_points = {}
    for merge_commit in merge_commits:
        cmd = f"git log -n 1 --pretty=format:'%cd' --date=iso {merge_commit}"
        branch_commit_date = run_git_command(cmd).strip()
        branch_points[merge_commit] = datetime.fromisoformat(branch_commit_date)
    return branch_points


def calculate_differences(
    merge_commits: dict[str, datetime], branch_points: dict[str, datetime]
):
    """Calculate the time differences between merging and branch points."""
    differences = []
    for merge_commit, merge_date in merge_commits.items():
        if merge_commit in branch_points:
            cmd = f"git show -s --format=%ci --date=iso {merge_commit}"
            branch_date = datetime.fromisoformat(run_git_command(cmd).strip())
            difference = (merge_date - branch_date).days
            differences.append(difference)
    return differences


def calculate_statistics(differences):
    """Calculate and print statistical measures of the differences."""
    average_time = np.mean(differences)
    min_time = np.min(differences)
    max_time = np.max(differences)
    percentile_90 = np.percentile(differences, 90)

    print(f"Average Time: {average_time:.2f} days")
    print(f"Minimum Time: {min_time} days")
    print(f"Maximum Time: {max_time} days")
    print(f"90th Percentile Time: {percentile_90} days")


def main(path: Path, branch_name: str):
    chdir(path)
    merge_commits = get_merge_commits(branch_name)
    branch_points = get_branch_points(merge_commits)
    differences = calculate_differences(merge_commits, branch_points)
    calculate_statistics(differences)


if __name__ == "__main__":
    main(Path(sys.argv[1]), sys.argv[2])
