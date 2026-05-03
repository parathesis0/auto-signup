# 网页存活检测脚本

> **免责声明**：本脚本仅供学习交流，应当且只应该用于检测目标网页是否存活。若将本脚本用于其他任何用途，由此产生的一切后果由使用者自行承担，与本项目作者无关。

## 环境配置

建议使用 `venv`：

```bash
python3 -m venv .venv
source .venv/bin/activate   # Linux / macOS
# 或
.venv\Scripts\activate      # Windows
pip install -r requirements.txt
```

退出 `venv`：

```bash
deactivate
```

### 关于依赖

`requirements.txt` 包含两个 HTTP 库：

- `curl_cffi` — 自带浏览器 TLS 指纹模拟，推荐安装，否则 windows 平台无法成功
- `requests` — 作为 fallback，当 `curl_cffi` 不可用时自动使用

脚本运行时会自动检测：优先使用 `curl_cffi`，未安装则回退到 `requests`。两者均可正常工作。

## 使用说明

终端中执行 `python checkin.py`，跨平台，无需区分系统。
运行前最好把终端代理关一下。不确定是否有影响。

### 配置文件

首次使用前，编辑 `config.json` 填入账号信息：

```json
{
    "username": "学号",
    "password": "密码",
    "city": "城市",
    "district": "区县",
    "reason": "原因"
}
```

- `username` 和 `password` 必填
- `city`、`district`、`reason` 为不在校签到的预设值，填好后不在校签到时无需再手动输入

命令行参数优先级高于配置文件，可随时覆盖。

### 在校签到（默认）

配置好 `config.json` 后，直接运行：

```bash
python checkin.py
```

### 不在校签到

```bash
python checkin.py -s 不在校
```

城市、区县、原因从 `config.json` 读取。也可以命令行覆盖：

```bash
python checkin.py -s 不在校 --city 城市 --district 区县 --reason 原因
```

### 静默模式

添加 `--no-output` 参数：

```bash
python checkin.py --no-output
```

### 完整参数

| 参数 | 说明 | 必填 |
|---|---|---|
| `-u` / `--username` | 学号 | 配置文件已填则否 |
| `-p` / `--password` | 密码 | 配置文件已填则否 |
| `-s` / `--status` | 签到状态：`在校`（默认）或 `不在校` | 否 |
| `--city` | 不在校时的城市 | 不在校时必填 |
| `--district` | 不在校时的区县 | 不在校时必填 |
| `--reason` | 不在校原因 | 不在校时必填 |
| `--no-output` | 静默模式 | 否 |

### 定时运行

#### Linux / macOS（crontab）

```bash
crontab -e
```

添加一行（每天 22:00 运行）：

```
0 22 * * * cd /path/to/auto-signup && .venv/bin/python3 checkin.py --no-output
```

#### Windows（任务计划程序）

可配合 Windows 任务计划程序定时运行。
