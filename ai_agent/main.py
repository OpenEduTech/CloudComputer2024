import json

from flask import Flask, request, jsonify, render_template, redirect, url_for, session
from langchain_core.messages import HumanMessage
from obs import ObsClient

from config import OBS_ACCESS_KEY, OBS_SECRET_KEY, OBS_BUCKET_NAME, Endpoint
from teacher.Chinese_agent import app_chinese
from teacher.English_agent import app_english
from teacher.Math_agent import app_math
from teacher.suggestion_agent import app_suggestion


def get_response(app, query):
    input_messages = [HumanMessage(query)]
    config = {"configurable": {"thread_id": "abc123"}}
    output = app.invoke({"messages": input_messages}, config)
    return output["messages"][-1].content


def choose_app(app_choice):
    if app_choice == '1':
        return app_math
    elif app_choice == '2':
        return app_chinese
    elif app_choice == '3':
        return app_english


app = Flask(__name__)

# 设置 Flask 应用的 secret_key
app.secret_key = '123456'  # 替换为一个唯一的密钥

# 创建OBS客户端
obs_client = ObsClient(
    access_key_id=OBS_ACCESS_KEY,
    secret_access_key=OBS_SECRET_KEY,
    server=Endpoint)

config = {
    "ak": OBS_ACCESS_KEY,
    "sk": OBS_SECRET_KEY
}


def save_user(user_id, user_data):
    """
    将用户数据保存到OBS中
    :param user_id: 用户ID
    :param user_data: 用户数据（字典）
    """
    object_key = f'users/{user_id}.json'
    user_data_json = json.dumps(user_data)
    resp = obs_client.putContent(bucketName=OBS_BUCKET_NAME, objectKey=object_key, content=user_data_json)
    if resp.status < 300:
        print(f"User {user_id} saved successfully.")
    else:
        print(f"Failed to save user {user_id}. Error: {resp.error_code} {resp.error_msg}")


def load_user(user_id):
    """
    从OBS中加载用户数据
    :param user_id: 用户ID
    :return: 用户数据（字典），如果用户不存在则返回None
    """
    object_key = f'users/{user_id}.json'
    try:
        resp = obs_client.getObject(bucketName=OBS_BUCKET_NAME, objectKey=object_key, loadStreamInMemory=True)
        if resp.status < 300:
            user_data_json = resp.body['buffer'].decode('utf-8')
            user_data = json.loads(user_data_json)
            return user_data
        else:
            return None
    except Exception as e:
        print(f"Exception occurred while loading user {user_id}: {e}")
        return None


# 首页：登录界面
@app.route('/')
def index():
    if 'username' in session:
        return redirect(url_for('dashboard'))
    return render_template('login.html')  # 登录页面


# 注册界面
@app.route('/register')
def register_page():
    return render_template('register.html')  # 注册页面


# 登录处理
@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    user = load_user(username)

    if user is None:
        return jsonify({"error": "用户名不存在，请注册后登录！"}), 400
    elif user['password'] != password:
        return jsonify({"error": "密码错误，请重试！"}), 400
    else:
        session['username'] = username  # 登录成功后将用户名存入 session
        return jsonify({"message": f"欢迎回来，{username}！"})


@app.route('/register', methods=['POST'])
def register():
    username = request.form['username']
    password = request.form['password']

    # 检查用户是否已存在
    user = load_user(username)

    if user is not None:
        print(f"User {username} already exists.")  # 调试信息
        return jsonify({"error": "用户名已存在，请选择其他用户名！"}), 400
    else:
        # 保存新用户数据，确保保存的是一个字典
        user_data = {"password": password}
        save_user(username, user_data)
        print(f"User {username} registered successfully with data: {user_data}")  # 调试信息
        return jsonify({"message": f"注册成功，欢迎您，{username}！"})


@app.route('/logout', methods=['GET'])
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))


# 仪表盘
@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('index'))
    return render_template('dashboard.html', username=session['username'])


@app.route('/get_response', methods=['POST'])
def get_response_route():
    data = request.form  # 修改为处理表单数据
    query = data.get('query')
    app_choice = data.get('app_choice')
    app = choose_app(app_choice)
    response = get_response(app, query)
    return jsonify({"response": response})


@app.route('/save_conversation', methods=['POST'])
def save_conversation():
    username = session['username']

    data = request.get_json()
    conversation = data.get('conversation')

    if not conversation:
        return jsonify({'error': '对话内容不能为空'}), 400

    object_key = f'users/{username}.json'

    try:
        resp = obs_client.getObject(
            bucketName=OBS_BUCKET_NAME, 
            objectKey=object_key, 
            loadStreamInMemory=True
        )

        if resp.status < 300:
            user_data_json = resp.body['buffer'].decode('utf-8')
            user_data = json.loads(user_data_json)
        else:
            user_data = {}

        if 'conversation' in user_data:
            user_data['conversation'] += '\n' + conversation
        else:
            user_data['conversation'] = conversation

        # 保存更新后的数据到 OBS
        obs_client.putContent(
            bucketName=OBS_BUCKET_NAME,
            objectKey=object_key,
            content=json.dumps(user_data)
        )

        return jsonify({'status': 'success'})

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/load_conversation', methods=['POST'])
def load_conversation():
    username = session['username']

    object_key = f'users/{username}.json'

    try:
        resp = obs_client.getObject(bucketName=OBS_BUCKET_NAME, objectKey=object_key, loadStreamInMemory=True)
        if resp.status < 300:
            conversation = json.loads(resp.body['buffer'].decode('utf-8'))
            c = conversation['conversation']
            return jsonify({'conversation': c})
        else:
            return jsonify({'error': f"加载对话失败: {resp.error_code} {resp.error_msg}"}), 400
    except Exception as e:
        print(f"加载对话时出错: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/delete_conversation', methods=['POST'])
def delete_conversation():
    username = session.get('username')

    if not username:
        return jsonify({'error': '用户未登录'}), 403

    object_key = f'users/{username}.json'

    try:
        # 尝试删除OBS中的对象
        resp = obs_client.deleteObject(
            bucketName=OBS_BUCKET_NAME, 
            objectKey=object_key
        )
        if resp.status < 300:
            return jsonify({'status': 'success'})
        else:
            return jsonify({'error': f"删除对话失败: {resp.error_code} {resp.error_msg}"}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/get_learning_suggestion', methods=['POST'])
def get_learning_suggestion():
    username = session['username']

    object_key = f'users/{username}.json'

    try:
        resp = obs_client.getObject(bucketName=OBS_BUCKET_NAME, objectKey=object_key, loadStreamInMemory=True)
        if resp.status < 300:
            conversation = json.loads(resp.body['buffer'].decode('utf-8'))
            c = conversation.get('conversation', '')
            prompt = f"{c}\n给我生成对应的语文数学和英语学习建议"
            response = get_response(app_suggestion, prompt)
            return jsonify({"suggestion": response})
        else:
            return jsonify({'error': f"加载对话失败: {resp.error_code} {resp.error_msg}"}), 400
    except Exception as e:
        print(f"加载对话时出错: {e}")
        return jsonify({'error': str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)
