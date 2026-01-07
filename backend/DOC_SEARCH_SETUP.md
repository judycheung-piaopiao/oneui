# ONE UI - Document Search Setup

## ✅ Phase 1 Complete: Basic RAG Implementation

文档搜索功能已经成功实现！现在你可以对工具文档进行语义搜索。

---

## 🚀 快速开始

### 1. 安装新依赖

```bash
cd backend
uv sync
```

这会安装以下新包：
- `chromadb` - 向量数据库
- `beautifulsoup4` - HTML 解析
- `lxml` - XML/HTML 处理器

### 2. 启动服务器

```bash
uv run main.py
```

服务器会自动加载 AI 模型（首次启动需要下载约 100MB）。

---

## 📖 API 使用指南

### 查看完整文档

访问：http://localhost:8000/docs

### 核心 API 端点

#### 1️⃣ 索引单个工具的文档

```bash
# 为某个工具建立文档索引
POST http://localhost:8000/api/index-tool-docs/{tool_id}

# 示例
curl -X POST http://localhost:8000/api/index-tool-docs/strategy-gui-v2
```

**什么时候用：**
- 新增工具后
- 文档更新后
- 单个工具需要重新索引

#### 2️⃣ 索引所有工具文档

```bash
# 一次性索引所有工具的文档（后台任务）
POST http://localhost:8000/api/reindex-all-docs

# 示例
curl -X POST http://localhost:8000/api/reindex-all-docs
```

**什么时候用：**
- 首次设置系统
- 批量更新所有文档
- 定期刷新索引（建议每天一次）

#### 3️⃣ 搜索文档内容

```bash
# 语义搜索文档
GET http://localhost:8000/api/doc-search?q={query}&limit=10&min_score=0.3

# 示例
curl "http://localhost:8000/api/doc-search?q=如何部署+strategy+GUI&limit=5"
```

**搜索示例：**
- `"如何部署 strategy GUI"` - 中文搜索
- `"RKV connection troubleshooting"` - 英文搜索
- `"配置文件在哪里"` - 找配置说明
- `"authentication setup"` - 找认证文档

**返回结果：**
```json
{
  "query": "如何部署 strategy GUI",
  "results": [
    {
      "tool_id": "strategy-gui-v2",
      "tool_name": "Strategy GUI v2",
      "content_snippet": "部署步骤：1. 安装依赖 npm install 2. 启动后端 node server.js...",
      "doc_url": "https://confluence.company.com/strategy-gui",
      "doc_type": "confluence",
      "relevance_score": 0.876
    }
  ],
  "total": 1
}
```

#### 4️⃣ 查看索引统计

```bash
# 查看当前索引了多少文档
GET http://localhost:8000/api/doc-stats

# 示例
curl http://localhost:8000/api/doc-stats
```

**返回示例：**
```json
{
  "total_chunks": 245,
  "total_tools": 15,
  "model_dimension": 384
}
```

#### 5️⃣ 删除工具的文档索引

```bash
# 删除某个工具的所有文档片段
DELETE http://localhost:8000/api/index-tool-docs/{tool_id}

# 示例
curl -X DELETE http://localhost:8000/api/index-tool-docs/old-tool
```

---

## 🔧 工作原理

### 文档处理流程

```
1. 抓取文档
   └─> Confluence 页面 / README 文件
   
2. 提取文本
   └─> 移除 HTML 标签、导航栏等
   
3. 分块（Chunking）
   └─> 每块 ~500 字符，有重叠
   
4. 向量化（Embedding）
   └─> 使用多语言 AI 模型
   
5. 存储到 ChromaDB
   └─> 向量数据库，支持语义搜索
   
6. 搜索
   └─> 用户查询 → 向量化 → 相似度匹配 → 返回结果
```

### 支持的文档类型

✅ **Confluence 页面**
- 自动识别主要内容区域
- 移除导航栏、侧边栏

✅ **Markdown 文件**
- README.md
- 技术文档

✅ **普通网页**
- HTML 页面
- 自动提取主要内容

---

## 🎯 实际使用场景

### 场景 1：首次设置

```bash
# 1. 启动服务器
uv run main.py

# 2. 索引所有现有工具的文档
curl -X POST http://localhost:8000/api/reindex-all-docs

# 等待几分钟...

# 3. 检查索引状态
curl http://localhost:8000/api/doc-stats

# 4. 测试搜索
curl "http://localhost:8000/api/doc-search?q=deployment"
```

### 场景 2：添加新工具后

```python
# 在创建工具后立即索引文档
import requests

# 创建工具
tool_data = {
    "name": "New Tool",
    "documentation_link": "https://confluence.company.com/new-tool"
}
response = requests.post("http://localhost:8000/api/tools", json=tool_data)
tool_id = response.json()["id"]

# 索引文档
requests.post(f"http://localhost:8000/api/index-tool-docs/{tool_id}")
```

### 场景 3：定期更新索引

```bash
# 使用 cron job 每天凌晨 2 点更新
0 2 * * * curl -X POST http://localhost:8000/api/reindex-all-docs
```

---

## 📊 与现有 AI 搜索的区别

| 功能 | 现有 AI 搜索 | 新的文档搜索 |
|------|--------------|--------------|
| 搜索范围 | 工具名称、描述、标签 | **完整文档内容** |
| 数据来源 | 工具元数据 | Confluence、README |
| 搜索深度 | 浅层匹配 | **深度语义理解** |
| 使用场景 | "找到 strategy 工具" | "如何部署 strategy" |

**两者互补使用：**
- 快速找工具 → 用 `/api/ai-search`
- 查找使用方法 → 用 `/api/doc-search`

---

## 🧪 测试示例

### Python 测试脚本

```python
import requests

BASE_URL = "http://localhost:8000/api"

# 1. 索引文档
response = requests.post(f"{BASE_URL}/index-tool-docs/strategy-gui-v2")
print("索引状态:", response.json())

# 2. 搜索文档
params = {
    "q": "如何连接 RKV 服务器",
    "limit": 5,
    "min_score": 0.3
}
response = requests.get(f"{BASE_URL}/doc-search", params=params)
results = response.json()

print(f"\n找到 {results['total']} 个结果：")
for r in results['results']:
    print(f"- {r['tool_name']}: {r['content_snippet'][:100]}...")
    print(f"  相关度: {r['relevance_score']}")
```

### JavaScript 测试

```javascript
// 搜索文档
async function searchDocs(query) {
  const response = await fetch(
    `http://localhost:8000/api/doc-search?q=${encodeURIComponent(query)}&limit=10`
  );
  const data = await response.json();
  return data.results;
}

// 使用
const results = await searchDocs("deployment guide");
console.log(results);
```

---

## 📁 数据存储位置

```
backend/
├── data/
│   ├── chroma_db/          ← 向量数据库（自动创建）
│   │   ├── chroma.sqlite3  ← 元数据
│   │   └── *.bin           ← 向量数据
│   └── tools.json          ← 工具数据
```

**注意：** `chroma_db` 文件夹会自动创建，首次运行时会下载 AI 模型。

---

## ⚠️ 常见问题

### Q1: 模型下载失败？

```bash
# 手动预下载模型
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')"
```

### Q2: 索引速度太慢？

- 正常：每个文档 2-5 秒
- 加速：减少文档长度或增加服务器资源

### Q3: 搜索结果不准确？

- 调整 `min_score` 参数（默认 0.3）
- 重新索引文档
- 检查文档质量

### Q4: 内存不足？

- ChromaDB 会持久化存储，重启不会丢失数据
- 考虑使用更小的模型或清理旧索引

---

## 🎉 完成了什么

✅ 文档向量化系统（RAG）
✅ 多语言语义搜索（中英文）
✅ Confluence 页面爬取
✅ 自动文档分块
✅ 后台异步索引
✅ 完整 REST API

---

## 🚀 下一步建议

### 立即可做：
1. ✅ 运行 `uv sync` 安装依赖
2. ✅ 启动服务器测试
3. ✅ 索引一两个工具文档试试
4. ✅ 在前端集成搜索界面

### Phase 2（可选增强）：
- 定时自动更新索引
- 支持 PDF 文档
- 搜索结果高亮显示
- 搜索历史记录

### Phase 3（高级功能）：
- 集成 OpenAI/Claude 做对话式问答
- 多轮对话支持
- 引用来源链接

需要我帮你实现任何一项吗？
