#!/usr/bin/env python3
"""
Clawpool 状态上报脚本
装在各台电脑上，自动上报 AI 助手状态到 MongoDB
"""
import os
import sys
import json
import socket
import datetime
import psutil
import requests

# ========== 配置 ==========
# MongoDB 连接地址
MONGO_URI = os.environ.get("MONGO_URI", "mongodb+srv://mongojianguo:02tF3LjCcn6oa6dw@jianguo.pboosfo.mongodb.net/clawpool")

# 本机标识 (改成你电脑的名字)
DEVICE_NAME = os.environ.get("DEVICE_NAME", socket.gethostname())

# OpenClaw 路径 (根据实际修改)
OPENCLAW_DIR = os.environ.get("OPENCLAW_DIR", "/home/ybuntu/.openclaw")


def get_system_status():
    """获取本机系统状态"""
    try:
        cpu = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        return {
            "cpu_percent": cpu,
            "memory_percent": memory.percent,
            "memory_used_gb": round(memory.used / (1024**3), 1),
        }
    except:
        return {}


def get_openclaw_status():
    """获取 OpenClaw 状态"""
    status = {}
    
    # 检查 openclaw.json
    config_file = os.path.join(OPENCLAW_DIR, "openclaw.json")
    if os.path.exists(config_file):
        try:
            with open(config_file, "r") as f:
                config = json.load(f)
                agents = config.get("agents", {})
                defaults = agents.get("defaults", {})
                status["model"] = defaults.get("model", "unknown")
        except:
            pass
    
    # 检查 session pool
    session_file = os.path.join(OPENCLAW_DIR, "session_pool.json")
    if os.path.exists(session_file):
        try:
            with open(session_file, "r") as f:
                sessions = json.load(f)
                status["active_sessions"] = len(sessions.get("sessions", []))
        except:
            pass
    
    return status


def get_claw_data():
    """组装要上报的龙虾数据"""
    system = get_system_status()
    openclaw = get_openclaw_status()
    
    return {
        "name": "建国",
        "platform": DEVICE_NAME,
        "emoji": "🦞",
        "status": "active",
        "role": "AI 助手",
        "cpu": system.get("cpu_percent", 0),
        "memory": system.get("memory_percent", 0),
        "model": openclaw.get("model", "unknown"),
        "sessions": openclaw.get("active_sessions", 0),
        "lastActive": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
        "updatedAt": datetime.datetime.now().isoformat(),
    }


def report_status():
    """上报状态到 MongoDB"""
    try:
        from pymongo import MongoClient
        client = MongoClient(MONGO_URI)
        db = client["clawpool"]
        claws = db.claws
        
        claw = get_claw_data()
        
        # 用 platform 作为唯一标识，更新或插入
        result = claws.update_one(
            {"platform": DEVICE_NAME},
            {"$set": claw},
            upsert=True
        )
        
        print(f"✅ [{DEVICE_NAME}] 状态已上报")
        print(f"   CPU: {claw['cpu']}% | 内存: {claw['memory']}%")
        print(f"   会话数: {claw['sessions']}")
        return True
        
    except Exception as e:
        print(f"❌ 上报失败: {e}")
        return False


if __name__ == "__main__":
    print(f"📡 正在上报 {DEVICE_NAME} 状态到虾池...")
    report_status()
