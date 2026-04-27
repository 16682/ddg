from http.server import BaseHTTPRequestHandler
import json
import subprocess
import os

class handler(BaseHTTPRequestHandler):
    # 封装一个发送跨域 Header 的辅助方法
    def _send_cors_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')

    # 处理浏览器的预检请求 (非常重要，解决跨域的核心)
    def do_OPTIONS(self):
        self.send_response(200)
        self._send_cors_headers()
        self.end_headers()

    def do_POST(self):
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            req_body = json.loads(post_data.decode('utf-8'))

            account = req_body.get('account')
            password = req_body.get('password')
            steps = req_body.get('steps', '20000')

            root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            script_path = os.path.join(root_dir, 'main.py')

            env = os.environ.copy()
            config_dict = {
                "USER": account,
                "PWD": password,
                "MIN_STEP": str(steps),
                "MAX_STEP": str(steps),
                "SLEEP_GAP": "5",
                "USE_CONCURRENT": "False"
            }
            env["CONFIG"] = json.dumps(config_dict)
            env["AES_KEY"] = "1234567890abcdef"

            result = subprocess.run(
                ['python', script_path],
                env=env,
                capture_output=True,
                text=True,
                cwd=root_dir
            )

            # 返回成功结果 (加入跨域头)
            self.send_response(200)
            self._send_cors_headers()
            self.send_header('Content-type', 'application/json; charset=utf-8')
            self.end_headers()
            
            response_data = {
                "code": 200,
                "message": "执行完毕",
                "log": result.stdout,
                "error": result.stderr
            }
            self.wfile.write(json.dumps(response_data, ensure_ascii=False).encode('utf-8'))

        except Exception as e:
            # 报错时也要加入跨域头
            self.send_response(500)
            self._send_cors_headers()
            self.send_header('Content-type', 'application/json; charset=utf-8')
            self.end_headers()
            self.wfile.write(json.dumps({"code": 500, "error": str(e)}).encode('utf-8'))

    def do_GET(self):
        self.send_response(200)
        self._send_cors_headers()
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write("<h1>MiMotion API 运行正常！</h1><p>请使用 POST 方法请求此接口并携带 JSON 参数。</p>".encode('utf-8'))
