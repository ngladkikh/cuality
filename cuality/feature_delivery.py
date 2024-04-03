import subprocess
from datetime import datetime, timedelta
import sys
from os import chdir
from pathlib import Path

import numpy as np


def run_git_command(command: str) -> list[str]:
    return subprocess.check_output(command, shell=True, text=True).strip().split("\n")


def get_merge_commits(branch_name: str) -> dict[str, list[str]]:
    """Gets all merge commits from a specified branch."""
    command = f"git log {branch_name} --merges --pretty=format:'%H %P'"
    merges = run_git_command(command)
    # Return a dict with merge commit as key and parents as value
    return {commit.split()[0]: commit.split()[1:] for commit in merges}


def get_branch_points(merge_commits: dict[str, list[str]], trunk_branch: str) -> dict[str, str]:
    """Finds branch points for each merge commit."""
    branch_points = {}
    for merge_commit, parents in merge_commits.items():
        if len(parents) > 1:  # Ensure it's a merge commit with two parents
            # First parent is the trunk's side of the merge
            trunk_parent = parents[0]
            # Attempt to approximate the branch point as the common ancestor
            # of the trunk parent just before the merge and the trunk branch itself
            # This is an approximation and might not work in all cases
            command = f"git merge-base {trunk_parent} {trunk_branch}"
            branch_point = run_git_command(command)
            branch_points[merge_commit] = branch_point[0]
    return branch_points


def calculate_differences(branch_points: dict[str, str]) -> list[float]:
    """Calculates the time differences between branch creation and merging."""
    differences: list[float] = []
    for merge_commit, parent in branch_points.items():
        merge_date = run_git_command(f"git show -s --format=%ci {merge_commit}")[0]
        branch_date = run_git_command(f"git show -s --format=%ci {parent}")[0]
        merge_datetime = datetime.fromisoformat(merge_date)
        branch_datetime = datetime.fromisoformat(branch_date)
        difference = (merge_datetime - branch_datetime).total_seconds()
        differences.append(difference)
    return differences


def calculate_statistics(differences: list[float]) -> None:
    """Calculates and prints statistics based on time differences."""
    average_time = timedelta(seconds=np.mean(differences))
    min_time = timedelta(seconds=np.min(differences))
    max_time = timedelta(seconds=np.max(differences))
    percentile_90 = timedelta(seconds=np.percentile(differences, 90))
    print(f"Average Time: {average_time}")
    print(f"Minimum Time: {min_time}")
    print(f"Maximum Time: {max_time}")
    print(f"90th Percentile Time: {percentile_90}")


def main(path: Path, branch_name: str):
    chdir(path)
    merge_commits = get_merge_commits(branch_name)
    branch_points = get_branch_points(merge_commits, branch_name)
    differences = calculate_differences(branch_points)
    calculate_statistics(differences)


if __name__ == "__main__":
    main(Path(sys.argv[1]), sys.argv[2])
