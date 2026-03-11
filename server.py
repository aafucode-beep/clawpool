"""
Clawpool 龙虾池子 - 后端 API 服务
记录各个平台的 AI 助手（龙虾）
"""
import os
import json
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse
import datetime

# MongoDB 配置 - 使用环境变量
MONGO_URI = os.environ.get("MONGO_URI", "")
DATABASE_NAME = "clawpool"

try:
    from pymongo import MongoClient
    client = MongoClient(MONGO_URI)
    db = client[DATABASE_NAME]
    claws = db.claws
    # Test connection
    client.admin.command('ping')
    MONGO_OK = True
    print("MongoDB 连接成功")
except Exception as e:
    MONGO_OK = False
    print(f"MongoDB 连接失败: {e}")
    # 使用内存存储作为后备
    claws_data = []

# 腾讯 COS 配置（可选）- 使用环境变量
COS_CONFIG = {
    "secret_id": os.environ.get("TENCENT_SECRET_ID", ""),
    "secret_key": os.environ.get("TENCENT_SECRET_KEY", ""),
    "bucket": os.environ.get("COS_BUCKET", "clawpool"),
    "region": os.environ.get("COS_REGION", "ap-shanghai"),
}


def get_all_claws():
    """获取所有龙虾"""
    if MONGO_OK:
        return list(claws.find({}, {"_id": 0}))
    return claws_data


def get_claw(platform):
    """根据平台获取单只龙虾"""
    if MONGO_OK:
        return claws.find_one({"platform": platform}, {"_id": 0})
    for claw in claws_data:
        if claw.get("platform") == platform:
            return claw
    return None


def add_claw(data):
    """添加新龙虾"""
    if MONGO_OK:
        data["created_at"] = datetime.datetime.now().isoformat()
        claws.insert_one(data)
        return {"success": True}
    claws_data.append(data)
    return {"success": True}


def update_claw(platform, data):
    """更新龙虾信息"""
    if MONGO_OK:
        result = claws.update_one(
            {"platform": platform},
            {"$set": data}
        )
        return {"success": result.modified_count > 0}
    for i, claw in enumerate(claws_data):
        if claw.get("platform") == platform:
            claws_data[i].update(data)
            return {"success": True}
    return {"success": False}


# API 路由处理
def handle_api(path):
    parsed = urlparse(path)
    path = parsed.path
    
    if path == "/api/claws":
        return get_all_claws()
    elif path.startswith("/api/claw/"):
        platform = path.split("/")[-1]
        return get_claw(platform)
    elif path == "/api/tech-stack":
        return {
            "project": "Clawpool 龙虾池子",
            "version": "1.0",
            "platform": "Vercel + MongoDB Atlas",
            "storage": "腾讯 COS",
            "built_by": "建国 🦞",
            "description": "记录各平台 AI 助手"
        }
    
    return {"error": "Not Found"}


class ClawpoolHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=os.path.join(os.path.dirname(__file__), "public"), **kwargs)
    
    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        
        if path.startswith("/api/"):
            data = handle_api(path)
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8"))
        elif path == "/" or path == "":
            self.path = "/index.html"
            super().do_GET()
        else:
            super().do_GET()
    
    def log_message(self, format, *args):
        pass


if __name__ == "__main__":
    import socket
    PORT = int(os.environ.get("PORT", 8080))
    local_ip = socket.gethostbyname(socket.gethostname())
    
    server = HTTPServer(("0.0.0.0", PORT), ClawpoolHandler)
    print(f"🦞 Clawpool 运行中:")
    print(f"   本地: http://127.0.0.1:{PORT}")
    print(f"   局域网: http://{local_ip}:{PORT}")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n已停止")
        server.server_close()
