from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index_chat.html')

@app.route('/send_message', methods=['POST'])
def send_message():
    user_message = request.form.get('user_message')
    # 在实际应用中，你可以在这里进行一些处理，并生成相应的回复
    server_response = f'已收到消息: "{user_message}"'
    return jsonify({'user_message': user_message, 'server_response': server_response})

if __name__ == '__main__':
    app.run(debug=True)
