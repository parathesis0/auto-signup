# 网页存活检测脚本

> **免责声明**：本脚本仅供学习交流，应当且只应该用于检测目标网页是否存活。若将本脚本用于其他任何用途，由此产生的一切后果由使用者自行承担，与本项目作者无关。

## 环境配置

建议使用 `venv`：

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

退出 `venv`：

```bash
deactivate
```

## 脚本说明

本项目提供两个版本的脚本，请根据运行环境选择：

| 脚本 | 适用环境 | HTTP 库 |
|---|---|---|
| `checkin_linux.py` | Linux / WSL | `requests` |
| `checkin_windows.py` | Windows | `curl_cffi` |

## 使用说明

### Linux / WSL

创建密码文件：

```bash
echo -n '密码' > password.txt
chmod 600 password.txt
```

运行一次：

```bash
python3 checkin_linux.py -u 学号 -p $(cat password.txt)
```

静默模式（无输出）：

```bash
python3 checkin_linux.py -u 学号 -p $(cat password.txt) --no-output
```

#### 定时运行（crontab）

```bash
crontab -e
```

添加一行（每天 22:00 运行）：

```
0 22 * * * cd /path/to/auto-signup && .venv/bin/python3 checkin_linux.py -u 学号 -p $(cat /path/to/password.txt) --no-output
```

### Windows

```powershell
py checkin_windows.py -u 学号 -p 密码
```

静默模式：

```powershell
py checkin_windows.py -u 学号 -p 密码 --no-output
```

可配合 Windows 任务计划程序定时运行。

运行前最好把控制台代理关一下。不确定是否有影响。
