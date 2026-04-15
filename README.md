# 自动签到脚本

## 环境配置

建议使用 `venv` ：

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
```

退出 `venv` ：

```bash
deactivate
```

## 使用说明

### Linux

可以使用以下指令，在当前目录下创建一个`password.txt`的文件，里面一行，是你账号的密码：

```bash
echo -n '密码' > password.txt
chmod 600 password.txt
```

运行以下指令可以完成一次签到：

```bash
python3 main.py -u 学号 -p $(cat password.txt)
```

如果你不希望产生任何输出，可以加上`--no-output`：

```bash
python3 main.py -u 学号 -p $(cat ./password.txt) --no-output
```

可以用`crontab`等方法定时运行脚本。

#### crontab

```bash
crontab -u 用户名 -e
```

添加一行（每天22:00运行）：

```
0 22 * * * python3 /path/to/main.py -u 学号 -p $(cat /path/to/password.txt) --no-output
```

保存即可。

### Windows

建议自行研究。
