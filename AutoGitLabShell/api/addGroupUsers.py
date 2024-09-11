import requests
import urllib3

# 禁用 SSL 警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 极狐 GitLab 的 URL 和个人访问令牌
gitlab_url = "https://192.168.1.125/api/v4"
access_token = "mytoken"

# 群组 ID
group_id = 848

# Git 地址文件路径
users_file_path = 'D:/AutoGitLabShell/api/groupusers.txt'

headers = {
    "Private-Token": access_token,
    "Content-Type": "application/json"
}

# 读取 Git 地址文件
with open(users_file_path, 'r', encoding='utf-8') as file:
    users = [line.strip().split(',') for line in file]

# 将用户添加到群组
for user_info in users:
    if len(user_info) != 4:
        print(f"无效的用户信息行: {','.join(user_info)}")
        continue
    
    _,_,username, _ = user_info
     # 验证用户是否存在
    response = requests.get(f"{gitlab_url}/users?username={username}", headers=headers, verify=False)
    
    if response.status_code == 200:
        user_data = response.json()
        if user_data:
            user_id = user_data[0]['id']
            
            response = requests.delete(f"{gitlab_url}/groups/{group_id}/members/{user_id}", headers=headers, verify=False)
            if response.status_code == 201:
                print(f"群组用户 {username} 删除成功")
            else:
                print(f"群组用户 {username} 删除失败，状态码: {response.status_code}, 响应: {response.text}")
            # 将用户添加到群组
            payload = {
                "user_id": user_id,
                "access_level": 40 
            }
            # 无访问权限（0）
            # 最小访问权限（5）（引入于 13.5）
            # 访客（10）
            # 报告者（20）
            # 开发者（30）
            # 维护者（40）
            # 拥有者（50）（对 14.9 及更高版本中的项目有效）
            
            response = requests.post(f"{gitlab_url}/groups/{group_id}/members", headers=headers, json=payload, verify=False)
            
            if response.status_code == 201:
                print(f"用户 {username} 添加到群组成功")
            else:
                print(f"添加用户 {username} 到群组失败，状态码: {response.status_code}, 响应: {response.text}")
        else:
            print(f"用户 {username} 不存在")
    else:
        print(f"验证用户 {username} 是否存在失败，状态码: {response.status_code}, 响应: {response.text}")