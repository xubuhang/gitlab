import requests
import urllib3

# 禁用 SSL 警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 极狐 GitLab 的 URL 和个人访问令牌
gitlab_url = "https://192.168.1.125/api/v4"
access_token = "mytoken"

headers = {
    "Private-Token": access_token,
    "Content-Type": "application/json"
}

def get_all_users():
    """获取所有非管理员用户的信息"""
    all_users = []
    page = 1
    per_page = 1000  # 每页返回的用户数量

    while True:
        url = f"{gitlab_url}/users?per_page={per_page}&page={page}"
        response = requests.get(url, headers=headers, verify=False)
        
        if response.status_code != 200:
            print(f"获取用户信息失败，状态码: {response.status_code}")
            break
        
        users = response.json()
        if not users:
            break
        
         # 过滤非管理员且非 ghost 用户
        non_admin_non_ghost_users = [user for user in users if not user.get('is_admin', False) and not user.get('is_guest', False)]
        all_users.extend(non_admin_non_ghost_users)
        page += 1
    
    return all_users

def delete_user(user_id):
    """删除指定ID的用户，并执行硬删除"""
    url = f"{gitlab_url}/users/{user_id}?hard_delete=true"
    response = requests.delete(url, headers=headers, verify=False)
    
    if response.status_code == 204:
        print(f"成功硬删除用户 {user_id}")
    else:
        print(f"硬删除用户 {user_id} 失败，状态码: {response.status_code}")

def main():
    # 获取所有用户信息
    all_users = get_all_users()
    
    # 遍历每个用户并删除
    for user in all_users:
        user_id = user['id']
        delete_user(user_id)

if __name__ == "__main__":
    main()
