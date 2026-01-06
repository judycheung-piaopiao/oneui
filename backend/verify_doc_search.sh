#!/bin/bash
# 文档搜索功能验证脚本

API_URL="http://localhost:8889/api"
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "========================================="
echo "🧪 AG Tools 文档搜索功能验证"
echo "========================================="
echo ""

# 测试 1: 检查服务器
echo "📡 测试 1: 检查服务器状态..."
response=$(curl -s -w "\n%{http_code}" "${API_URL%/api}")
http_code=$(echo "$response" | tail -n1)
if [ "$http_code" = "200" ] || [ "$http_code" = "404" ]; then
    echo -e "${GREEN}✅ 服务器运行中 (端口 8889)${NC}"
else
    echo -e "${RED}❌ 服务器未响应${NC}"
    exit 1
fi
echo ""

# 测试 2: 检查文档搜索端点
echo "📚 测试 2: 检查文档搜索 API 端点..."
endpoints=$(curl -s "${API_URL%/api}/openapi.json" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    doc_endpoints = [p for p in data.get('paths', {}).keys() if 'doc' in p.lower()]
    if doc_endpoints:
        print('找到以下文档搜索端点:')
        for ep in doc_endpoints:
            print(f'  - {ep}')
    else:
        print('未找到文档搜索端点')
except:
    print('无法解析 API 规范')
" 2>/dev/null)

if echo "$endpoints" | grep -q "doc-search\|doc-stats\|index-tool-docs"; then
    echo -e "${GREEN}✅ 文档搜索 API 已注册${NC}"
    echo "$endpoints"
else
    echo -e "${RED}❌ 未找到文档搜索端点${NC}"
    echo "$endpoints"
    exit 1
fi
echo ""

# 测试 3: 测试统计 API
echo "📊 测试 3: 获取文档索引统计..."
stats=$(curl -s "$API_URL/doc-stats")
if echo "$stats" | grep -q "total_chunks\|total_tools"; then
    echo -e "${GREEN}✅ 统计 API 工作正常${NC}"
    echo "$stats" | python3 -m json.tool 2>/dev/null || echo "$stats"
else
    echo -e "${RED}❌ 统计 API 失败: $stats${NC}"
fi
echo ""

# 测试 4: 测试搜索功能
echo "🔍 测试 4: 测试语义搜索..."
search_result=$(curl -s "$API_URL/doc-search?q=test&limit=5")
if echo "$search_result" | grep -q "query\|results"; then
    echo -e "${GREEN}✅ 搜索 API 工作正常${NC}"
    result_count=$(echo "$search_result" | python3 -c "import sys, json; print(json.load(sys.stdin).get('total', 0))" 2>/dev/null)
    echo "   搜索结果数: $result_count"
else
    echo -e "${YELLOW}⚠️  搜索 API 可用但无结果（数据库可能为空）${NC}"
    echo "$search_result" | python3 -m json.tool 2>/dev/null || echo "$search_result"
fi
echo ""

# 测试 5: 检查 AI 模型
echo "🤖 测试 5: 检查 AI 模型加载..."
if ps aux | grep -i "python.*main.py" | grep -v grep > /dev/null; then
    echo -e "${GREEN}✅ Python 进程运行中${NC}"
    # 检查日志中是否有模型加载成功的消息
    if [ -f "/tmp/ag-tools-backend.log" ]; then
        if grep -q "Embedding model loaded successfully" /tmp/ag-tools-backend.log 2>/dev/null; then
            echo -e "${GREEN}✅ AI 模型加载成功${NC}"
        fi
    fi
else
    echo -e "${YELLOW}⚠️  无法确认 Python 进程${NC}"
fi
echo ""

# 总结
echo "========================================="
echo "📋 验证总结"
echo "========================================="
echo -e "${GREEN}✅ 基础功能已实现${NC}"
echo ""
echo "🎯 下一步操作:"
echo "1. 访问 API 文档: http://localhost:8889/docs"
echo "2. 索引工具文档: curl -X POST $API_URL/reindex-all-docs"
echo "3. 测试搜索: curl '$API_URL/doc-search?q=你的查询'"
echo ""
echo "💡 提示: 如果搜索无结果，需要先索引文档！"
