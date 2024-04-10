import sys
from pathlib import Path

import requests
import csv


def fetch_pull_requests(repo: str, token: str):
    url = f"https://api.github.com/repos/{repo}/pulls"
    with requests.Session() as session:
        session.headers.update({"Authorization": f"token {token}"})
        while url:
            response = session.get(url, params={"state": "all", "per_page": 100})
            response.raise_for_status()
            yield from response.json()
            link_header = response.headers.get("Link", None)
            if link_header:
                links = {
                    rel.split("; ")[1][5:-1]: rel.split("; ")[0][1:-1]
                    for rel in link_header.split(", ")
                }
                url = links.get("next", None)
            else:
                break


def extract_pr_data(prs):
    data = []
    for pr in prs:
        pr_id = pr["id"]
        creator = pr["user"]["login"]
        target_branch = pr["base"]["ref"]
        created_at = pr["created_at"]
        status = (
            "merged"
            if pr["merged_at"]
            else "declined" if pr["state"] == "closed" else pr["state"]
        )
        merged_or_declined_at = pr["merged_at"] if pr["merged_at"] else pr["closed_at"]
        data.append(
            [pr_id, creator, target_branch, created_at, status, merged_or_declined_at]
        )
    return data


def write_to_csv(pr_data: list, file: Path) -> None:
    headers = [
        "PR ID",
        "Creator",
        "Target Branch",
        "Created At",
        "Status",
        "Merged/Declined At",
    ]
    with open(file, "w", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(headers)
        writer.writerows(pr_data)


def read_github_pr_data(
    repo: str, token: str, output: Path = Path("pull_requests.csv")
) -> None:
    pr_data = extract_pr_data(fetch_pull_requests(repo, token))
    write_to_csv(pr_data, output)
    print(f"Successfully written PR data to pull_requests.csv")


if __name__ == "__main__":
    read_github_pr_data(sys.argv[1], sys.argv[2])
