# QuickForm 在 Windows 上的部署方式

以下均为 Windows 可用方案。**推荐生产环境用 Waitress + IIS（或 NSSM 常驻）**，避免“约 6 小时不响应”。

---

## 方案一：Waitress（推荐，多线程防卡死）

[Waitress](https://docs.pylonsproject.org/projects/waitress/) 多线程，单个请求卡住不会拖死整站，适合 7×24 运行。

### 安装

```cmd
pip install waitress
```

（已写入 `requirements.txt`，可 `pip install -r requirements.txt`。）

### 启动（HTTP 8000）

在项目根目录执行其一即可：

```cmd
python run_waitress.py
```

或：

```cmd
python -m waitress --host=0.0.0.0 --port=8000 --call app:app
```

- 默认监听 **8000**，可通过环境变量改：`WAITRESS_PORT=9000`、`WAITRESS_THREADS=8`。
- Waitress **不直接支持 SSL**，对外 443 需由 IIS 或 Nginx 做反向代理（见方案四）。

### 对外仍用 443 + 证书（IIS 反向代理）

1. 用 NSSM 或计划任务让 `python run_waitress.py` 常驻，监听 `127.0.0.1:8000`（或 `0.0.0.0:8000`）。
2. 在 IIS 里为 quickform.cn 绑定 443、挂你的证书，用 **URL 重写 / ARR** 把请求转发到 `http://127.0.0.1:8000`。
3. 80 端口可在 IIS 做 301 重定向到 https。

这样：浏览器访问 `https://quickform.cn` → IIS 解 SSL → 转发到 Waitress 8000，单请求卡住不会拖死整站。

### 暂时不配 IIS 时

- 可继续用 **`python app.py`** 跑 443（Flask 自带 SSL），不享受 Waitress 多线程，但无需改现有架构。
- 或只跑 **`python run_waitress.py`** 做内网/测试：访问 `http://服务器:8000`。

---

## 方案二：直接运行（当前做法）

在项目根目录、**以管理员身份**打开 PowerShell 或 CMD：

```cmd
python app.py
```

- 使用 `app.py` 里配置的端口（默认 443）和 SSL 证书。
- 关掉窗口或断开远程桌面后进程会结束，适合临时测试。

---

## 方案三：NSSM 做成 Windows 服务（推荐 7×24）

[NSSM](https://nssm.cc/) 把任意可执行程序注册为系统服务：开机自启、用户注销后仍运行、可配置“崩溃后自动重启”。

### 1. 下载 NSSM

从 https://nssm.cc/download 解压到例如 `C:\nssm`。

### 2. 安装服务（管理员 CMD）

```cmd
cd C:\nssm\win64
nssm install QuickForm
```

在弹出窗口里：

- **Path**：`C:\Python311\python.exe`（改成你本机 python 路径，可用 `where python` 查）
- **Startup directory**：你的 QuickForm 项目根目录
- **Arguments**（二选一）：
  - 用 **Waitress**（推荐）：`run_waitress.py` 或 `-m waitress --host=0.0.0.0 --port=8000 --call app:app`
  - 用 Flask 自带 443+SSL：`app.py`

### 3. 可选：把输出写入日志

在 NSSM 窗口的 **I/O** 标签：

- **Output (stdout)**：`C:\QuickForm\app.log`
- **Error (stderr)**：同上或单独文件
- 勾选 **Append**，避免覆盖

### 4. 启动 / 停止 / 开机自启

```cmd
nssm start QuickForm
nssm stop QuickForm
nssm set QuickForm Start SERVICE_AUTO_START
```

服务名可在“服务”里看到，设为自动启动后重启电脑也会自动跑。

---

## 方案四：IIS + HttpPlatformHandler（反向代理）

IIS 监听 80/443、挂证书、做 80→443 跳转，把请求转发给本机一个端口的 Flask/Waitress 进程。

### 1. 安装

- 启用 IIS（控制面板 → 程序 → 启用或关闭 Windows 功能 → Internet Information Services）。
- 安装 [HttpPlatformHandler](https://www.iis.net/downloads/microsoft/httpplatformhandler) 或 [ASP.NET Core 托管捆绑包](https://dotnet.microsoft.com/download/dotnet)（内含托管模块）。

### 2. 用 NSSM 或计划任务常驻一个进程

例如用 Waitress 监听 `http://127.0.0.1:8000`，并设为开机启动（NSSM 或任务计划程序）。

### 3. IIS 站点绑定与 web.config

- 网站绑定：443，证书选你的 quickform.cn 证书；80 可重定向到 443。
- 站点根目录放一个 `web.config`，用 HttpPlatformHandler 把请求转发到 `http://127.0.0.1:8000`。

示例 `web.config`（放在站点物理路径根目录）：

```xml
<?xml version="1.0" encoding="utf-8"?>
<configuration>
  <system.webServer>
    <handlers>
      <add name="httpPlatform" path="*" verb="*" modules="httpPlatformHandler" resourceType="Unspecified" />
    </handlers>
    <httpPlatform processPath="C:\Python311\python.exe"
                  arguments="-m waitress --host=127.0.0.1 --port=8000 --call app:app"
                  stdoutLogEnabled="true"
                  stdoutLogFile="C:\QuickForm\logs\python.log"
                  startupTimeLimit="20"
                  startupRetryCount="3">
      <environmentVariables>
        <environmentVariable name="PYTHONPATH" value="D:\OneDrive\09教育技术处\QuickForm" />
      </environmentVariables>
    </httpPlatform>
  </system.webServer>
</configuration>
```

`processPath` / `arguments` / `PYTHONPATH` 按你本机路径和是否用 waitress 修改。这样 IIS 负责 80/443 和证书，Flask 只跑 HTTP 8000。

---

## 方案五：批处理 + 计划任务“开机自启”

不装 NSSM 时，可用计划任务在开机时运行一个批处理，在后台启动 Flask：

`start_quickform.bat`（放在项目根目录）：

```batch
@echo off
cd /d "D:\OneDrive\09教育技术处\QuickForm"
python app.py >> C:\QuickForm\app.log 2>&1
```

- 在“任务计划程序”里新建任务：触发器选“计算机启动时”，操作选“启动程序”并指定该 bat。
- 缺点：用户注销后由该用户启动的进程可能被结束，不如 NSSM 服务稳。更适合“一直保持同一用户登录”的机器。

---

## 小结

| 方式           | 适用场景           | 稳定性 / 备注                    |
|----------------|--------------------|----------------------------------|
| `python app.py`| 临时跑、本机 443+SSL | 关窗口即停                       |
| Waitress       | 长时间跑、多请求   | 比 Flask 自带稳，不直接支持证书   |
| NSSM 服务      | 7×24、开机自启     | 推荐，注销/重启后仍运行          |
| IIS + 反向代理 | 已有 IIS、统一 80/443 | 证书和 80→443 在 IIS 上配置     |
| 计划任务 + bat | 简单开机自启       | 依赖当前用户会话，不如 NSSM 稳   |

你当前已经用 `python app.py` 在 443 上跑且证书正常的话，**优先建议加一层 NSSM**，把现有 `python app.py` 注册为服务，这样“约 6 小时停”后也能自动拉起来（若再停可再查日志和事件查看器）。
