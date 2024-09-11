import requests
import urllib3
import re
import time

# 禁用 SSL 警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 极狐 GitLab 的 URL 和个人访问令牌
gitlab_url = "https://192.168.1.125/api/v4"
access_token = "mytoken"

# Git 地址文件路径
git_urls_file_path = 'D:/AutoGitLabShell/api/git_urls.txt'

headers = {
    "Private-Token": access_token,
    "Content-Type": "application/json"
}

# 读取 Git 地址文件
with open(git_urls_file_path, 'r', encoding='utf-8') as file:
    git_urls = [line.strip() for line in file]

# 去重
git_urls = list(set(git_urls))

# 获取群组 ID
def get_group_id(path):
    parts = path.split('/')
    current_group = None
    
    appendStr=''
    for part in parts:
       id = None
       appendStr += "/"+part

       if current_group is not None:
            id = current_group['id']
       current_group = create_group( part,id,appendStr)
    return current_group['id']

# 获取或创建子群组
def getgroup(appendStr=None):
    response = requests.get(f"{gitlab_url}/groups?per_page=10000", headers=headers, verify=False)
    if response.status_code == 200:
        groups = response.json()
        for group in groups:
            fullPath = "/"+group['full_path']
            if (group['full_path'] == appendStr or  fullPath== appendStr) :
                return group
    return None

# 创建群组
def create_group(path,parent_id=None,appendStr=None):
    payload = {
        "name": path,
        "path": path,
        "parent_id":parent_id
    }
    response = requests.post(f"{gitlab_url}/groups", headers=headers, json=payload, verify=False)
    if response.status_code == 201:
        return response.json()
    elif response.status_code == 400 and "已经被使用" in response.text:
        # 如果群组已存在，直接返回已存在的群组信息
        return getgroup(appendStr)
    else:
        raise Exception(f"Failed to create group {path}. Error: {response.text}")


# 创建项目
def create_project(group_id, name):
    payload = {
        "name": name.lower(),
        "namespace_id": group_id
    }
    response = requests.post(f"{gitlab_url}/projects", headers=headers, json=payload, verify=False)
    if response.status_code == 201:
        return response.json()
    elif response.status_code == 400 and "已经被使用" in response.text:
        # 如果项目已存在，直接返回已存在的项目信息
        return get_project_by_path(group_id, name.lower())
    else:
        raise Exception(f"Failed to create project {name}. Error: {response.text}")

# 获取指定路径的项目
def get_project_by_path(group_id, path):
    response = requests.get(f"{gitlab_url}/projects?search={path}&namespace_id={group_id}", headers=headers, verify=False)
    if response.status_code == 200:
        projects = response.json()
        for project in projects:
            if project['path'] == path and project['namespace']['id'] == group_id:
                return project
    raise Exception(f"Project {path} under namespace {group_id} does not exist.")

# 解析 Git 地址并创建群组和项目
for url in git_urls:
    match = re.match(r"https://192\.168\.1\.123/(.*)/(.*).git", url)
    if match:
        group_path = match.group(1).replace('/', '/').title()  # 确保每个部分首字母大写
        project_name = match.group(2).lower()  # 项目名称全部小写
        
        try:
            group_id = get_group_id(group_path)
            print(f"Group {group_path} already exists with ID {group_id}.")
        except Exception as e:
                print(f"Error: {e}")
            # else:
                # group_id = get_group_id(group_path)
                # print(f"Group {group_path} created successfully with ID {group_id}.")
        
        try:
            create_project(group_id, project_name)
            print(f"Project {project_name} created successfully.")
        except Exception as e:
            if "Failed to create project" in str(e):
                print(f"Project {project_name} already exists.")
            else:
                print(f"Failed to create project {project_name}. Error: {e}")
        
        # 每次请求后增加延迟
        # time.sleep(1)  # 休眠 1 秒
