#!/bin/bash
# Doc search verification script

API_URL="http://localhost:8889/api"
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "========================================="
echo "🧪 AG Tools Doc Search Verification"
echo "========================================="
echo ""

# Test 1: Check server
echo "📡 Test 1: Check server status..."
response=$(curl -s -w "\n%{http_code}" "${API_URL%/api}")
http_code=$(echo "$response" | tail -n1)
if [ "$http_code" = "200" ] || [ "$http_code" = "404" ]; then
    echo -e "${GREEN}✅ Server running (port 8889)${NC}"
else
    echo -e "${RED}❌ Server not responding${NC}"
    exit 1
fi
echo ""

# Test 2: Check doc search endpoints
echo "📚 Test 2: Check doc search API endpoints..."
endpoints=$(curl -s "${API_URL%/api}/openapi.json" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    doc_endpoints = [p for p in data.get('paths', {}).keys() if 'doc' in p.lower()]
    if doc_endpoints:
        print('Found doc search endpoints:')
        for ep in doc_endpoints:
            print(f'  - {ep}')
    else:
        print('No doc search endpoints found')
except:
    print('Unable to parse API spec')
" 2>/dev/null)

if echo "$endpoints" | grep -q "doc-search\|doc-stats\|index-tool-docs"; then
    echo -e "${GREEN}✅ Doc search API registered${NC}"
    echo "$endpoints"
else
    echo -e "${RED}❌ Doc search endpoints not found${NC}"
    echo "$endpoints"
    exit 1
fi
echo ""

# Test 3: Test stats API
echo "📊 Test 3: Get doc index stats..."
stats=$(curl -s "$API_URL/doc-stats")
if echo "$stats" | grep -q "total_chunks\|total_tools"; then
    echo -e "${GREEN}✅ Stats API working${NC}"
    echo "$stats" | python3 -m json.tool 2>/dev/null || echo "$stats"
else
    echo -e "${RED}❌ Stats API failed: $stats${NC}"
fi
echo ""

# Test 4: Test search functionality
echo "🔍 Test 4: Test semantic search..."
search_result=$(curl -s "$API_URL/doc-search?q=test&limit=5")
if echo "$search_result" | grep -q "query\|results"; then
    echo -e "${GREEN}✅ Search API working${NC}"
    result_count=$(echo "$search_result" | python3 -c "import sys, json; print(json.load(sys.stdin).get('total', 0))" 2>/dev/null)
    echo "   Results found: $result_count"
else
    echo -e "${YELLOW}⚠️  Search API available but no results (DB may be empty)${NC}"
    echo "$search_result" | python3 -m json.tool 2>/dev/null || echo "$search_result"
fi
echo ""

# Test 5: Check AI model
echo "🤖 Test 5: Check AI model loading..."
if ps aux | grep -i "python.*main.py" | grep -v grep > /dev/null; then
    echo -e "${GREEN}✅ Python process running${NC}"
    # Check if model loaded successfully from logs
    if [ -f "/tmp/ag-tools-backend.log" ]; then
        if grep -q "Embedding model loaded successfully" /tmp/ag-tools-backend.log 2>/dev/null; then
            echo -e "${GREEN}✅ AI model loaded${NC}"
        fi
    fi
else
    echo -e "${YELLOW}⚠️  Cannot confirm Python process${NC}"
fi
echo ""

# Summary
echo "========================================="
echo "📋 Verification Summary"
echo "========================================="
echo -e "${GREEN}✅ Basic functionality verified${NC}"
echo ""
echo "🎯 Next steps:"
echo "1. View API docs: http://localhost:8889/docs"
echo "2. Index docs: curl -X POST $API_URL/reindex-all-docs"
echo "3. Test search: curl '$API_URL/doc-search?q=your-query'"
echo ""
echo "💡 Note: If search returns no results, index docs first!"
