#!/usr/bin/env python3
"""
Clawpool 状态上报脚本
从 OpenClaw 电脑收集状态，报送到 MongoDB
"""
import os
import json
import socket
import datetime
import psutil
from pymongo import MongoClient

# 配置
MONGO_URI = "mongodb+srv://mongojianguo:02tF3LjCcn6oa6dw@jianguo.pboosfo.mongodb.net/clawpool"
DEVICE_NAME = socket.gethostname()

# 可选：手动设置的简介 (直接写死，或者从文件读取)
INTRO_FILE = os.path.expanduser("~/.clawpool_intro")
if os.path.exists(INTRO_FILE):
    with open(INTRO_FILE) as f:
        INTRO = f.read().strip()
else:
    INTRO = "靠谱、直接的 AI 助手"

# OpenClaw 路径 (根据实际修改)
OPENCLAW_DIR = os.path.expanduser("~/.openclaw")

def get_openclaw_info():
    """从 OpenClaw 获取信息"""
    info = {
        "model": "unknown",
        "sessions": 0,
        "skills": 0,
        "cronjobs": 0,
        "uptime": "unknown",
        "channel": "unknown",
        "app_id": "unknown",
    }
    
    # 1. 模型名称
    config_file = os.path.join(OPENCLAW_DIR, "openclaw.json")
    if os.path.exists(config_file):
        try:
            with open(config_file) as f:
                config = json.load(f)
                # 模型
                model = config.get("agents", {}).get("defaults", {}).get("model", "unknown")
                if isinstance(model, dict):
                    info["model"] = model.get("primary", str(model))
                else:
                    info["model"] = model
                # 通讯渠道
                channels = config.get("channels", {})
                if channels:
                    info["channel"] = list(channels.keys())[0]  # 取第一个渠道
                    # 飞书 APP ID
                    first_channel = list(channels.values())[0]
                    if "accounts" in first_channel:
                        accounts = first_channel["accounts"]
                        if "default" in accounts:
                            info["app_id"] = accounts["default"].get("appId", "unknown")
        except:
            pass
    
    # 2. 活跃会话数
    session_file = os.path.join(OPENCLAW_DIR, "session_pool.json")
    if os.path.exists(session_file):
        try:
            with open(session_file) as f:
                sessions = json.load(f)
                info["sessions"] = len(sessions.get("sessions", []))
        except:
            pass
    
    # 3. Skills 数量
    skills_dir = os.path.join(OPENCLAW_DIR, "skills")
    if os.path.exists(skills_dir):
        try:
            info["skills"] = len([f for f in os.listdir(skills_dir) if f.endswith('.md')])
        except:
            pass
    
    # 4. Cron 任务数
    cron_file = os.path.join(OPENCLAW_DIR, "cron", "jobs.json")
    if os.path.exists(cron_file):
        try:
            with open(cron_file) as f:
                jobs = json.load(f)
                info["cronjobs"] = len(jobs.get("jobs", []))
        except:
            pass
    
    # 5. 系统运行时间
    try:
        boot_time = psutil.boot_time()
        uptime_seconds = datetime.datetime.now().timestamp() - boot_time
        days = int(uptime_seconds // 86400)
        hours = int((uptime_seconds % 86400) // 3600)
        minutes = int((uptime_seconds % 3600) // 60)
        if days > 0:
            info["uptime"] = f"{days}天{hours}小时"
        else:
            info["uptime"] = f"{hours}小时{minutes}分钟"
    except:
        pass
    
    return info

def get_status():
    """组装要上报的数据"""
    oc = get_openclaw_info()
    
    return {
        "name": "建国",           # AI 助手名字
        "platform": DEVICE_NAME,  # 电脑名 (唯一标识)
        "emoji": "🦞",
        "status": "active",
        "role": "AI 助手",
        "intro": INTRO,           # 简介（可手动编辑）
        
        # 系统信息
        "cpu": round(psutil.cpu_percent(interval=1), 1),
        "memory": round(psutil.virtual_memory().percent, 1),
        
        # OpenClaw 信息
        "model": oc["model"],
        "channel": oc["channel"],
        "app_id": oc["app_id"],
        "sessions": oc["sessions"],
        "skills": oc["skills"],
        "cronjobs": oc["cronjobs"],
        "uptime": oc["uptime"],
        
        # 时间
        "lastActive": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
    }

def report():
    """上报到 MongoDB"""
    client = MongoClient(MONGO_URI)
    db = client["clawpool"]
    claws = db.claws
    
    data = get_status()
    claws.update_one(
        {"platform": DEVICE_NAME},
        {"$set": data},
        upsert=True
    )
    
    print(f"✅ {DEVICE_NAME}")
    print(f"   CPU: {data['cpu']}% | 内存: {data['memory']}%")
    print(f"   模型: {data['model']}")
    print(f"   渠道: {data['channel']}")
    print(f"   会话: {data['sessions']} | Skills: {data['skills']} | Cron: {data['cronjobs']}")
    print(f"   运行时间: {data['uptime']}")

if __name__ == "__main__":
    report()
