# 解决 Confluence 认证问题

## 🔐 问题说明

当前爬取 Confluence 页面时，返回的是登录页面内容：
```
"ONE UI Enter your credentials Save Details Login Login with Google..."
```

这是因为 Confluence 需要认证才能访问。

---

## ✅ 解决方案

我已经更新了系统，支持三种方式：

### **方案 1: Confluence API Token（推荐）** ⭐

**优点：**
- 最可靠，不依赖 JavaScript
- 直接获取纯文本内容
- 官方 API 支持

**步骤：**

1. **生成 API Token**
   - 访问：https://id.atlassian.com/manage-profile/security/api-tokens
   - 点击 "Create API token"
   - 给 token 命名（如 "AG Tools Crawler"）
   - 复制生成的 token

2. **配置环境变量**
   ```bash
   cd /home/jzhang/ag/gui-services/ag-tools-catalogue/backend
   
   # 创建 .env 文件
   cat > .env << 'EOF'
   HOST=0.0.0.0
   PORT=8889
   DEBUG=True
   
   # Confluence 认证
   CONFLUENCE_EMAIL=你的邮箱@company.com
   CONFLUENCE_API_TOKEN=粘贴你的token
   EOF
   ```

3. **重启服务器**
   ```bash
   # 停止旧进程
   pkill -f "python main.py"
   
   # 启动新进程
   nohup uv run python main.py > /tmp/ag-tools-backend.log 2>&1 &
   ```

4. **重新索引**
   ```bash
   curl -X POST http://localhost:8889/api/reindex-all-docs
   ```

---

### **方案 2: 公司内部 SSO**

如果 Confluence 使用 Google SSO 且在公司内网：

```bash
# 在公司网络内运行，可能会自动通过认证
# 或者配置 session cookies
```

---

### **方案 3: 使用 README 文件**

如果 Confluence 不可访问，可以索引 GitHub/Bitbucket 的 README：

```python
# 修改工具的 documentation_link 指向 README
{
  "documentation_link": "https://github.com/company/repo/blob/main/README.md"
}
```

---

## 🧪 验证认证是否成功

运行这个测试：

```bash
python3 << 'EOF'
import requests

# 测试 Confluence API
base_url = "https://your-confluence.com"
email = "your-email@company.com"
token = "your-api-token"

response = requests.get(
    f"{base_url}/rest/api/content",
    auth=(email, token),
    params={'limit': 1}
)

if response.status_code == 200:
    print("✅ 认证成功！")
    print(f"找到 {response.json()['size']} 个页面")
else:
    print(f"❌ 认证失败: {response.status_code}")
    print(response.text)
EOF
```

---

## 📊 更新后的效果

**之前（未认证）：**
```json
{
  "content_snippet": "ONE UI Enter your credentials Save Details Login..."
}
```

**之后（已认证）：**
```json
{
  "content_snippet": "Strategy GUI v2 是一个实时交易策略监控系统。部署步骤：1. 安装依赖..."
}
```

---

## 🚀 完整配置示例

```bash
# 1. 配置 .env
cat > /home/jzhang/ag/gui-services/ag-tools-catalogue/backend/.env << 'EOF'
HOST=0.0.0.0
PORT=8889
DEBUG=True

# Confluence 认证
CONFLUENCE_EMAIL=jzhang@company.com
CONFLUENCE_API_TOKEN=ATATT3xFfGF0Xxx...（你的 token）
EOF

# 2. 重启服务
pkill -f "python main.py"
cd /home/jzhang/ag/gui-services/ag-tools-catalogue/backend
nohup uv run python main.py > /tmp/ag-tools-backend.log 2>&1 &

# 3. 等待启动（15秒）
sleep 15

# 4. 重新索引所有文档
curl -X POST http://localhost:8889/api/reindex-all-docs

# 5. 等待索引完成（根据文档数量，可能需要几分钟）
sleep 60

# 6. 测试搜索
curl "http://localhost:8889/api/doc-search?q=deployment" | python3 -m json.tool

# 7. 查看统计
curl http://localhost:8889/api/doc-stats | python3 -m json.tool
```

---

## ⚡ 快速测试

```bash
# 测试单个工具的索引（替换 tool-id）
curl -X POST http://localhost:8889/api/index-tool-docs/your-tool-id

# 30秒后搜索
sleep 30
curl "http://localhost:8889/api/doc-search?q=你的搜索词" | python3 -m json.tool
```

如果看到真实的文档内容而不是登录页面，说明认证成功！✅

---

## 📞 获取帮助

需要我帮你：
1. 生成 Confluence API token？
2. 配置 .env 文件？
3. 测试认证是否工作？

告诉我你需要哪一步！
