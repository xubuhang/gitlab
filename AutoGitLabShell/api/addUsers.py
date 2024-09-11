import requests
import urllib3

# 禁用 SSL 警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 极狐 GitLab 的 URL 和个人访问令牌
gitlab_url = "https://192.168.1.125/api/v4"
access_token = "mytoken"

# Git 地址文件路径
users_file_path = 'D:/AutoGitLabShell/api/users.txt'

headers = {
    "Private-Token": access_token,
    "Content-Type": "application/json"
}

# 读取 Git 地址文件
with open(users_file_path, 'r', encoding='utf-8') as file:
    users = [line.strip().split(',') for line in file]

# 创建 GitLab 用户
for user_info in users:
    if len(user_info) != 5:
        print(f"无效的用户信息行: {','.join(user_info)}")
        continue
    
    name, email, username,organization,job_title = user_info
    payload = {
        "email": email,
        "username": username,
        "name": name,
        "password": "pass1234",  # 设置默认密码
        "reset_password": False,
        "organization":organization,
        "job_title":job_title,
        "preferred_language": "zh_CN"
    }

    response = requests.post(f"{gitlab_url}/users", headers=headers, json=payload, verify=False)

    if response.status_code == 201:
        print(f"用户 {username} 创建成功")
    else:
        print(f"创建用户 {username} 失败，状态码: {response.status_code}, 响应: {response.text}")
