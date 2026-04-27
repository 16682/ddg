from http.server import BaseHTTPRequestHandler
import json
import subprocess
import os

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            # 1. 获取请求体中的数据
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            req_body = json.loads(post_data.decode('utf-8'))

            account = req_body.get('account')
            password = req_body.get('password')
            steps = req_body.get('steps', '20000')

            # 2. 获取项目根目录路径 (使得 API 能找到外层的 main.py)
            root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            script_path = os.path.join(root_dir, 'main.py')

            # 3. 拼装原项目需要的严格 JSON 格式的环境变量
            env = os.environ.copy()
            config_dict = {
                "USER": account,
                "PWD": password,
                "MIN_STEP": str(steps),
                "MAX_STEP": str(steps), # 强制最大和最小一致，实现精准修改
                "SLEEP_GAP": "5",
                "USE_CONCURRENT": "False"
            }
            env["CONFIG"] = json.dumps(config_dict)
            env["AES_KEY"] = "1234567890abcdef" # 提供一个默认密钥防止报错

            # 4. 执行原项目的 main.py
            result = subprocess.run(
                ['python', script_path],
                env=env,
                capture_output=True,
                text=True,
                cwd=root_dir # 确保在根目录下执行
            )

            # 5. 将执行日志作为 API 结果返回给用户
            self.send_response(200)
            self.send_header('Content-type', 'application/json; charset=utf-8')
            self.end_headers()
            
            response_data = {
                "code": 200,
                "message": "执行完毕",
                "log": result.stdout,    # 成功日志
                "error": result.stderr   # 报错日志(如果有)
            }
            self.wfile.write(json.dumps(response_data, ensure_ascii=False).encode('utf-8'))

        except Exception as e:
            # 捕获崩溃异常
            self.send_response(500)
            self.send_header('Content-type', 'application/json; charset=utf-8')
            self.end_headers()
            self.wfile.write(json.dumps({"code": 500, "error": str(e)}).encode('utf-8'))

    # 为了方便浏览器测试，顺手写一个 GET 请求的防懵逼提示
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write("<h1>MiMotion API 运行正常！</h1><p>请使用 POST 方法请求此接口并携带 JSON 参数。</p>".encode('utf-8'))
