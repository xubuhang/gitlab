from flask import Flask, request, jsonify
import traceback
import requests
import urllib3
# 禁用 SSL 警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
app = Flask(__name__)

# 企业微信Webhook URL
WECHAT_WEBHOOK_URL = ""

def send_to_wechat(message):
    """
    发送Markdown格式的消息到企业微信。
    """
    headers = {
        'Content-Type': 'application/json',
    }
    payload = {
        "msgtype": "markdown",
        "markdown": {
            "content": message,
            "mentioned_mobile_list": ["@all"]
        }
    }

    response = requests.post(WECHAT_WEBHOOK_URL, json=payload, headers=headers)
    if response.status_code != 200:
        print(f"Failed to send message to WeChat: {response.text}")
    else:
        print("Message sent to WeChat successfully")


def format_push_event(event_data):
    """
    格式化push事件的Markdown消息。
    """
    commit_message = event_data['commits'][0]['message']
    author_name = event_data['user_name']
    repo_name = event_data['repository']['name']
    branch_name = event_data['ref'].split('/')[-1]
    return f"""
> **Push Event**
>
> - **Repository**: {repo_name}
> - **Branch**: {branch_name}
> - **Author**: {author_name}
> - **Commit Message**: {commit_message}
"""

def format_merge_request_event(event_data):
    """
    格式化merge request事件的Markdown消息。
    """
    title = event_data['object_attributes']['title']
    source_branch = event_data['object_attributes']['source_branch']
    target_branch = event_data['object_attributes']['target_branch']
    url = event_data['object_attributes']['url']
    return f"""
> **Merge Request Event**
>
> - **Title**: {title}
> - **Source Branch**: {source_branch}
> - **Target Branch**: {target_branch}
> - **URL**: [{url}]({url})
"""

def format_repository_update_event(event_data):
    """
    格式化repository update事件的Markdown消息。
    """
    event_name = event_data['event_name']
    user_name = event_data['user_name']
    project_id = event_data['project_id']
    repo_name = event_data['project']['name']
    repo_web_url = event_data['project']['web_url']
    ref = event_data['ref'].split('/')[-1]
    before = event_data['changes'][0]['before']
    after = event_data['changes'][0]['after']

    if repo_name:
        return f"""
> **Repository Update Event**
>
> - **Repository**: {repo_name}
> - **URL**: [{repo_name}]({repo_web_url})
> - **User**: {user_name}
> - **Ref**: {ref}
> - **Before**: {before[:7]}
> - **After**: {after[:7]}
"""
    else:
        return f"""
> **Repository Update Event**
>
> - **Project ID**: {project_id}
> - **Ref**: {ref}
> - **Before**: {before[:7]}
> - **After**: {after[:7]}
"""

def handle_gitlab_event(event_data):
    event_type = event_data.get('event_type')
    if event_type is None:
         event_type =event_data.get('event_name')
    if event_type == 'push':
        message = format_push_event(event_data)
        print("Received push event:", event_data)
        send_to_wechat(message)
    elif event_type == 'merge_request':
        message = format_merge_request_event(event_data)
        print("Received merge request event:", event_data)
        send_to_wechat(message)
    elif event_type == 'repository_update':
        message = format_repository_update_event(event_data)
        print("Received repository update event:", event_data)
        send_to_wechat(message)
    else:
        print(f"Unknown event type: {event_type}")

@app.route('/gitlab-webhook', methods=['POST'])
def gitlab_webhook():
    try:
        # 获取请求数据
        event_data = request.get_json()
        if event_data is None:
            return jsonify({'error': 'Invalid JSON data'}), 400

        # 获取请求头中的事件类型
        event_type = request.headers.get('X-Gitlab-Event')
        if event_type is None:
            return jsonify({'error': 'Missing X-Gitlab-Event header'}), 400

        # 处理事件数据
        handle_gitlab_event(event_data)
        return jsonify({'status': 'success'}), 200
    except Exception as e:
        # 记录详细的错误信息
        print(f"Error occurred: {e}")
        print(traceback.format_exc())
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
