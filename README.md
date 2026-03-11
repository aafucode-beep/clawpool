# 🦞 Clawpool 龙虾池子

## 快速开始

### 1. 上报数据到 MongoDB

在每台运行 OpenClaw 的电脑上：

```bash
# 1. 复制脚本
cp report.py ~/.clawpool_report.py

# 2. 运行上报
python3 ~/.clawpool_report.py
```

### 2. 设置定时任务 (可选)

```bash
crontab -e
# 添加一行：每小时上报一次
0 * * * * /usr/bin/python3 ~/.clawpool_report.py
```

### 3. 查看虾池网站

访问: https://clawpool-pi.vercel.app

---

## 项目目标

在各台电脑上部署状态上报脚本，统一汇总到云端展示。

## 系统架构

```
┌─────────────────────────────────────────────┐
│            虾池网站 (Vercel)                │
│        https://clawpool-pi.vercel.app      │
└──────────────────────┬──────────────────────┘
                       │ 读取数据
                       ▼
┌─────────────────────────────────────────────┐
│           MongoDB Atlas (云数据库)          │
│            clawpool.claws 集合              │
└──────────────────────┬──────────────────────┘
                       │ 写入数据
   ┌──────────────────┼──────────────────┐
   ▼                  ▼                  ▼
┌────────┐        ┌────────┐        ┌────────┐
│ HUAWEI │        │ ybuntu │        │  其他  │
│  脚本   │        │  脚本   │        │  脚本   │
└────────┘        └────────┘        └────────┘
```

## 技术栈

| 服务 | 用途 | 地址 |
|------|------|------|
| Vercel | 前端托管 | vercel.com |
| MongoDB Atlas | 云数据库 | cloud.mongodb.com |
| GitHub | 代码仓库 | github.com |

## 部署步骤

### 1. 创建 MongoDB Atlas 数据库

1. 登录 https://cloud.mongodb.com
2. 创建免费集群 (Free Tier)
3. 创建数据库用户 (用户名/密码)
4. 创建数据库 `clawpool`，集合 `claws`
5. 获取连接字符串：
   ```
   mongodb+srv://<用户名>:<密码>@<集群地址>/clawpool
   ```

### 2. 创建 GitHub 仓库

1. 登录 https://github.com
2. 创建新仓库 `clawpool`
3. 获取仓库地址

### 4. 创建 Vercel 项目

1. 登录 https://vercel.com
2. Import GitHub 仓库
3. 添加环境变量：
   - `MONGO_URI` = MongoDB 连接字符串

### 5. 部署状态上报脚本

在每台电脑上：

```python
# report.py
import os
import json
import socket
import datetime
import psutil
from pymongo import MongoClient

MONGO_URI = "你的MongoDB连接字符串"  # 从步骤1获取
DEVICE_NAME = socket.gethostname()  # 或手动指定，如 "HUAWEI"

def get_claw_data():
    return {
        "name": "建国",  # AI 助手名字
        "platform": DEVICE_NAME,  # 电脑名
        "emoji": "🦞",
        "status": "active",
        "role": "AI 助手",
        "cpu": psutil.cpu_percent(interval=1),
        "memory": psutil.virtual_memory().percent,
        "sessions": 0,  # 可从 session_pool.json 读取
        "lastActive": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
    }

def report_status():
    client = MongoClient(MONGO_URI)
    db = client["clawpool"]
    claws = db.claws
    
    claw = get_claw_data()
    claws.update_one(
        {"platform": DEVICE_NAME},
        {"$set": claw},
        upsert=True
    )
    print(f"✅ 已上报 {DEVICE_NAME}")

if __name__ == "__main__":
    report_status()
```

### 6. 设置定时任务 (可选)

```bash
# 每小时自动上报
crontab -e
0 * * * * /usr/bin/python3 /path/to/report.py
```

## 数据格式

MongoDB 集合 `claws` 文档结构：

```json
{
  "name": "建国",           // AI 助手名字
  "platform": "yj",        // 电脑 hostname (唯一标识)
  "emoji": "🦞",
  "status": "active",
  "role": "AI 助手",
  "intro": "靠谱、直接的AI助手",  // 简介 (可手动编辑)
  "cpu": 5.0,              // CPU 使用率
  "memory": 40.5,          // 内存使用率
  "model": "minimax-cn/MiniMax-M2.5",  // AI 模型
  "channel": "feishu",     // 通讯渠道
  "app_id": "cli_xxx",     // 飞书 APP ID
  "sessions": 0,           // 活跃会话数
  "skills": 0,             // Skills 数量
  "cronjobs": 0,           // Cron 任务数
  "uptime": "8小时",       // 系统运行时间
  "lastActive": "2026-03-11 20:13"
}
```

## API 接口

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/claws` | GET | 获取所有龙虾 |
| `/api/claw/:platform` | GET | 获取单个龙虾 |

## 本地开发

```bash
# 克隆仓库
git clone https://github.com/你的账号/clawpool.git
cd clawpool

# 安装依赖
pip install pymongo psutil

# 修改 report.py 中的配置
# DEVICE_NAME = "你的电脑名"
# MONGO_URI = "你的连接字符串"

# 测试运行
python report.py
```

## 文件结构

```
clawpool/
├── api/
│   └── index.py       # Vercel Python API
├── public/
│   └── index.html     # 前端页面
├── report.py          # 状态上报脚本
├── requirements.txt   # Python 依赖
└── vercel.json        # Vercel 配置
```

---

*由建国 🦞 整理*
