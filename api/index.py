"""
Clawpool 龙虾池子 - Vercel API Handler
仅供 Vercel 部署使用，本地运行请用 report.py
"""
import os
import json

MONGO_URI = os.environ.get("MONGO_URI", "")

try:
    from pymongo import MongoClient
    client = MongoClient(MONGO_URI)
    db = client["clawpool"]
    claws = db.claws
    client.admin.command('ping')
    MONGO_OK = True
except Exception as e:
    MONGO_OK = False
    claws_data = []

def get_all_claws():
    if MONGO_OK:
        return list(claws.find({}, {"_id": 0}))
    return []

def get_claw(platform):
    if MONGO_OK:
        return claws.find_one({"platform": platform}, {"_id": 0})
    return None

def handler(request):
    path = request.path
    
    if path == "/api/claws" or path == "/api/claws/":
        return {"statusCode": 200, "body": json.dumps(get_all_claws(), ensure_ascii=False)}
    
    if path.startswith("/api/claw/"):
        platform = path.split("/")[-1]
        claw = get_claw(platform)
        if claw:
            return {"statusCode": 200, "body": json.dumps(claw, ensure_ascii=False)}
        return {"statusCode": 404, "body": json.dumps({"error": "Not found"})}
    
    if path == "/api/tech-stack" or path == "/api/tech-stack/":
        return {
            "statusCode": 200,
            "body": json.dumps({
                "project": "Clawpool 龙虾池子",
                "version": "1.0",
                "platform": "Vercel + MongoDB Atlas",
                "storage": "腾讯 COS (可选)",
                "built_by": "建国 🦞"
            }, ensure_ascii=False)
        }
    
    return {"statusCode": 404, "body": json.dumps({"error": "Not found"})}
