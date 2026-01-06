export interface Tool {
  id: string;
  name: string;
  description: string;
  icon?: string;
  tool_link: string;
  documentation_link?: string;
  tags: string[];
  created_at?: string;
  updated_at?: string;
  // 文档搜索相关字段
  doc_match?: {
    content_snippet: string;  // 匹配的文档片段
    relevance_score: number;  // 相关度分数
    doc_url: string;          // 文档URL
  };
}

export interface ToolCreate {
  name: string;
  description: string;
  icon?: string;
  tool_link: string;
  documentation_link?: string;
  tags: string[];
}
