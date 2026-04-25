import requests
import pandas as pd

def get_repo_stats(owner: str, repo: str) -> pd.DataFrame:
    """GitHub API로 레포 정보를 가져와 pandas로 정리"""
    url = f"https://api.github.com/repos/{owner}/{repo}"
    response = requests.get(url)
    data = response.json()

    stats = {
        "항목": ["스타 수", "포크 수", "이슈 수", "언어", "라이선스"],
        "값": [
            data.get("stargazers_count", 0),
            data.get("forks_count", 0),
            data.get("open_issues_count", 0),
            data.get("language", "N/A"),
            data.get("license", {}).get("name", "N/A") if data.get("license") else "N/A"
        ]
    }

    df = pd.DataFrame(stats)
    return df

if __name__ == "__main__":
    df = get_repo_stats("jeongwool", "auto-feedback-system")
    print(df.to_string(index=False))