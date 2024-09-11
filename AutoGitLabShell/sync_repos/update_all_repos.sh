#!/bin/bash

# 定义新的 IP 和端口
NEW_IP="192.168.1.125"
NEW_PORT="80"


# 递归查找所有 .git 目录
find_git_repos() {
    local dir=$1
    find "$dir" -type d -name .git | while read -r git_dir; do
        process_repo "$(dirname "$git_dir")"
    done
}

# 处理 Git 仓库
process_repo() {
    local repo_dir=$1
    
    # 进入子目录
    cd "$repo_dir"
    
    # 获取当前仓库的远程仓库信息
    echo "Current remote information:"
    REMOTE_INFO=$(git remote -v | grep origin | grep fetch | awk '{print $2}')
    echo "$REMOTE_INFO"
    
    # 解析原始 URL
    OLD_URL="$REMOTE_INFO"
    if [[ "$OLD_URL" =~ ^https:// ]]; then
        # 处理 HTTPS URL
        OLD_IP=$(echo "$OLD_URL" | cut -d'/' -f3 | cut -d':' -f1)
        OLD_PORT=$(echo "$OLD_URL" | cut -d'/' -f3 | cut -d':' -f2)
        if [ -z "$OLD_PORT" ]; then
            OLD_PORT="80"
        fi
        OLD_PATH=$(echo "$OLD_URL" | cut -d'/' -f4-)
    elif [[ "$OLD_URL" =~ ^git@ ]]; then
        # 处理 SSH URL
        OLD_IP=$(echo "$OLD_URL" | cut -d':' -f1 | cut -d'@' -f2)
        OLD_PORT=$(echo "$OLD_URL" | cut -d':' -f2 | cut -d'/' -f1)
        if [ -z "$OLD_PORT" ]; then
            OLD_PORT="22"
        fi
        OLD_PATH=$(echo "$OLD_URL" | cut -d':' -f2 | cut -d'/' -f2-)
    else
        echo "Unsupported URL format: $OLD_URL"
        return
    fi
    
    # 构建新的 URL
    NEW_URL="https://${NEW_IP}:${NEW_PORT}/${OLD_PATH}"
    echo "New URL: $NEW_URL"
    
    # 重命名远程仓库
    echo "Renaming remote origin to old-origin..."
    git remote rename origin old-origin
    
    # 添加新的远程仓库
    echo "Adding new remote origin..."
    git remote add origin "$NEW_URL"
    
    # 拉取新的远程仓库
    echo "Pulling from new remote origin..."
    git pull origin main --allow-unrelated-histories
    
    # 查看状态
    echo "Current status:"
    git status
    
    # 获取所有冲突文件
    CONFLICT_FILES=$(git ls-files -u | awk '{print $2}')
    
    # 保留本地版本并解决冲突
    echo "Resolving conflicts by keeping local changes..."
    for file in $CONFLICT_FILES; do
        git checkout --ours "$file"
        echo "Resolved conflict for file: $file"
    done
    
    # 添加解决后的文件
    echo "Adding resolved files..."
    git add $CONFLICT_FILES
    
    # 提交解决冲突的结果
    echo "Committing resolved conflicts..."
    git commit -m "Resolved merge conflicts by keeping local changes"
    
    # 推送所有分支
    echo "Pushing all branches..."
    git push --set-upstream origin --all
    
    # 推送所有标签
    echo "Pushing all tags..."
    git push --set-upstream origin --tags
    
    # 返回上级目录
    cd ..
}

# 开始从指定目录遍历
find_git_repos "D:/源代码"
