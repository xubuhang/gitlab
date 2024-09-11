import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

import re
# 极狐 GitLab 的 URL 和个人访问令牌
gitlab_url = "https://192.168.1.125/api/v4"
access_token = "mytoken"


headers = {
    "Private-Token": access_token,
    "Content-Type": "application/json"
}
# 获取所有项目的列表
def get_all_groups():
    all_groups = []
    page = 1
    per_page = 1000  # 每页返回的项目数量

    while True:
        response = requests.get(
            f"{gitlab_url}/groups?per_page=10000",
            params={"per_page": per_page, "page": page},
            headers=headers,
            verify=False
        )

        if response.status_code != 200:
            raise Exception(f"Failed to fetch groups. Error: {response.text}")

        groups = response.json()
        if not groups:
            break

        all_groups.extend(groups)
        page += 1

    return all_groups

# 删除单个项目
def delete_group(group_id):
    response = requests.delete(f"{gitlab_url}/groups/{group_id}", headers=headers,verify=False)
    if response.status_code != 202:
        raise Exception(f"Failed to delete group {group_id}. Error: {response.text}")
    print(f"Deleted group {group_id}.")

# 主程序
def main():
    try:
        all_groups = get_all_groups()
        print(f"Found {len(all_groups)} groups.")
        
        for group in all_groups:
            group_id = group["id"]
            delete_group(group_id)
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()