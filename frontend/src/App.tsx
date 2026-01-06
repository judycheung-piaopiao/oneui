import { useState, useEffect } from 'react';
import { 
  AppBar, 
  Toolbar, 
  Typography, 
  Container, 
  Box, 
  Button, 
  CircularProgress, 
  Alert,
  Chip,
  Stack,
  IconButton,
  Menu,
  MenuItem,
} from '@mui/material';
import { Settings, FilterList, SearchOff, AccountCircle, Logout, Psychology } from '@mui/icons-material';
import ToolCard from './components/ToolCard';
import SearchBar from './components/SearchBar';
import FilterSidebar from './components/FilterSidebar';
import AdminPage from './components/AdminPage';
import LoginPage from './components/LoginPage';
import ParticlesBackground from './components/ParticlesBackground';
import type { Tool } from './types';
import type { User } from './types/auth';
import { getTools, getAllTags, getCurrentUser, aiSearch, docSearch } from './api/tools';
import { isAdminRole } from './types/auth';
import './App.css';

function App() {
  const [tools, setTools] = useState<Tool[]>([]);
  const [filteredTools, setFilteredTools] = useState<Tool[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [allTags, setAllTags] = useState<string[]>([]);
  const [selectedTags, setSelectedTags] = useState<string[]>([]);
  const [showAdminPage, setShowAdminPage] = useState(false);
  const [showFilters, setShowFilters] = useState(true);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [user, setUser] = useState<User | null>(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [authChecking, setAuthChecking] = useState(true);
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const [aiLoading, setAiLoading] = useState(false);
  const [isAIResult, setIsAIResult] = useState(false);

  const loadData = async () => {
    try {
      setLoading(true);
      const [toolsData, tagsData] = await Promise.all([
        getTools(),
        getAllTags(),
      ]);
      setTools(toolsData);
      setAllTags(tagsData);
    } catch (error) {
      console.error('Failed to load data:', error);
      setError('Failed to load tools. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const filterTools = () => {
    let filtered = [...tools];

    if (searchQuery) {
      const query = searchQuery.toLowerCase().trim();
      
      // Filter and score results
      const scoredResults = tools.map((tool) => {
        const name = tool.name.toLowerCase();
        const description = tool.description.toLowerCase();
        const tags = tool.tags.map(t => t.toLowerCase());
        
        let score = 0;
        
        // Score 1000: Exact name match
        if (name === query) {
          score = 1000;
        }
        // Score 900: Name starts with query
        else if (name.startsWith(query)) {
          score = 900;
        }
        // Score 800: Name contains query
        else if (name.includes(query)) {
          score = 800;
        }
        // Score 700: Word in name starts with query
        else if (name.split(/[\s-_]+/).some(word => word.startsWith(query))) {
          score = 700;
        }
        // Score 500: Tag matches
        else if (tags.some(tag => tag.includes(query) || tag.startsWith(query))) {
          score = 500;
        }
        // Score 300: Description contains query
        else if (description.includes(query)) {
          score = 300;
        }
        // Score 200: Word in description starts with query
        else if (description.split(/[\s-_]+/).some(word => word.startsWith(query))) {
          score = 200;
        }
        
        return { tool, score };
      }).filter(item => item.score > 0);
      
      // Sort by score (highest first)
      filtered = scoredResults
        .sort((a, b) => b.score - a.score)
        .map(item => item.tool);
    }

    if (selectedTags.length > 0) {
      filtered = filtered.filter((tool) =>
        selectedTags.some((tag) => tool.tags.includes(tag))
      );
    }

    // Priority ordering when no search query
    if (!searchQuery) {
      const priorityOrder = ['ag trades db', 'ag cms', 'periscope'];
      filtered.sort((a, b) => {
        const aName = a.name.toLowerCase();
        const bName = b.name.toLowerCase();
        const aIndex = priorityOrder.indexOf(aName);
        const bIndex = priorityOrder.indexOf(bName);
        
        // If both in priority list, sort by priority order
        if (aIndex !== -1 && bIndex !== -1) {
          return aIndex - bIndex;
        }
        // If only a is in priority list, a comes first
        if (aIndex !== -1) return -1;
        // If only b is in priority list, b comes first
        if (bIndex !== -1) return 1;
        // Otherwise maintain original order
        return 0;
      });
    }

    setFilteredTools(filtered);
  };

  const handleAISearch = async () => {
    if (!searchQuery.trim()) {
      // If no search query, apply tag filters only
      if (selectedTags.length > 0) {
        const filtered = tools.filter((tool) =>
          selectedTags.some((tag) => tool.tags.includes(tag))
        );
        setFilteredTools(filtered);
      } else {
        setFilteredTools(tools);
      }
      return;
    }
    
    setAiLoading(true);
    try {
      // 同时调用两个搜索 API
      const [aiResponse, docResponse] = await Promise.all([
        aiSearch(searchQuery, 20),
        docSearch(searchQuery, 20)
      ]);
      
      // 处理 AI 搜索结果（基于工具元数据）
      const aiResults = aiResponse.results.map((r: any) => ({
        id: r.id,
        name: r.name,
        description: r.description,
        icon: r.icon,
        tool_link: r.tool_link,
        documentation_link: r.documentation_link,
        tags: r.tags,
      }));
      
      // 处理文档搜索结果（基于文档内容）
      // 对文档结果去重：同一工具可能有多个文档片段匹配，保留最高相关度的
      const docResultsMap = new Map<string, any>();
      for (const r of docResponse.results) {
        const existing = docResultsMap.get(r.tool_id);
        if (!existing || r.relevance_score > existing.relevance_score) {
          docResultsMap.set(r.tool_id, {
            id: r.tool_id,
            doc_match: {
              content_snippet: r.content_snippet,
              relevance_score: r.relevance_score,
              doc_url: r.doc_url,
            }
          });
        }
      }
      const docResults = Array.from(docResultsMap.values());
      
      // 合并结果：三种优先级排序
      // 1. 同时在 AI 和 Doc 结果中的（keyword + doc match）- 最相关
      // 2. 只在 AI 结果中的（keyword/description match）- 中等相关
      // 3. 只在 Doc 结果中的（doc match only）- 较低相关
      
      const aiResultIds = new Set(aiResults.map((r: any) => r.id));
      const docResultIds = new Set(docResults.map((r: any) => r.id));
      
      const bothMatchTools: Tool[] = [];  // 同时匹配
      const aiOnlyTools: Tool[] = [];     // 只有 AI 匹配（关键词/描述）
      const docOnlyTools: Tool[] = [];    // 只有文档匹配
      
      // 处理文档搜索结果
      for (const docResult of docResults) {
        const tool = tools.find(t => t.id === docResult.id);
        if (tool) {
          const toolWithDoc = {
            ...tool,
            doc_match: docResult.doc_match,
          };
          
          if (aiResultIds.has(docResult.id)) {
            // 同时在两个结果中
            bothMatchTools.push(toolWithDoc);
          } else {
            // 只在文档结果中
            docOnlyTools.push(toolWithDoc);
          }
        }
      }
      
      // 处理只在 AI 结果中的工具
      for (const aiResult of aiResults) {
        if (!docResultIds.has(aiResult.id)) {
          aiOnlyTools.push(aiResult);
        }
      }
      
      // 按优先级合并：bothMatch -> aiOnly -> docOnly
      let mergedResults = [...bothMatchTools, ...aiOnlyTools, ...docOnlyTools];
      
      // Apply tag filters on merged results
      if (selectedTags.length > 0) {
        mergedResults = mergedResults.filter((tool: Tool) =>
          selectedTags.some((tag) => tool.tags.includes(tag))
        );
      }
      
      setFilteredTools(mergedResults);
      setIsAIResult(true);
    } catch (error) {
      console.error('AI search failed:', error);
      setError('AI search temporarily unavailable, using regular search');
      filterTools();
      setIsAIResult(false);
    } finally {
      setAiLoading(false);
    }
  };

  const handleSearchChange = (value: string) => {
    setSearchQuery(value);
    setIsAIResult(false);
  };

  const handleTagToggle = (tag: string) => {
    setSelectedTags((prev) =>
      prev.includes(tag) ? prev.filter((t) => t !== tag) : [...prev, tag]
    );
  };

  // Check authentication on mount
  useEffect(() => {
    // Skip authentication for development
    setIsAuthenticated(true);
    setAuthChecking(false);
    setUser({ 
      user_id: 1,
      first_name: 'Dev',
      last_name: 'User',
      email: 'dev@local', 
      role_name: 'ADMIN',
      team_name: 'Development',
      active: true,
      username: 'dev'
    } as User);
    loadData();
  }, []);

  useEffect(() => {
    if (isAIResult) {
      // If showing AI results, reapply AI search with new filters
      handleAISearch();
    } else {
      filterTools();
    }
  }, [tools, searchQuery, selectedTags]);

  const checkAuth = async () => {
    const token = localStorage.getItem('access_token');
    if (!token) {
      setAuthChecking(false);
      setIsAuthenticated(false);
      return;
    }

    try {
      const userData = await getCurrentUser();
      setUser(userData);
      setIsAuthenticated(true);
    } catch (error) {
      console.error('Auth check failed:', error);
      localStorage.removeItem('access_token');
      setIsAuthenticated(false);
    } finally {
      setAuthChecking(false);
    }
  };

  const handleLoginSuccess = (token: string) => {
    checkAuth();
  };

  const handleLogout = () => {
    localStorage.removeItem('access_token');
    setUser(null);
    setIsAuthenticated(false);
    setAnchorEl(null);
  };

  const handleMenuOpen = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
  };

  // Show login page if not authenticated
  if (authChecking) {
    return (
      <Box sx={{ 
        display: 'flex', 
        justifyContent: 'center', 
        alignItems: 'center', 
        minHeight: '100vh',
        background: 'linear-gradient(135deg, #0a0e27 0%, #1a1f3a 100%)',
      }}>
        <CircularProgress 
          size={60} 
          sx={{
            color: '#10b981',
            '& .MuiCircularProgress-circle': {
              strokeLinecap: 'round',
            },
          }}
        />
      </Box>
    );
  }

  if (!isAuthenticated) {
    return <LoginPage onLoginSuccess={handleLoginSuccess} />;
  }

  if (showAdminPage) {
    return <AdminPage onBack={() => { setShowAdminPage(false); loadData(); }} />;
  }

  return (
    <>
      <ParticlesBackground />
      <Box sx={{ 
        display: 'flex', 
        flexDirection: 'column', 
        minHeight: '100vh',
        position: 'relative',
        '&::before': {
          content: '""',
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          background: 'radial-gradient(circle at 20% 50%, rgba(16, 185, 129, 0.1) 0%, transparent 50%), radial-gradient(circle at 80% 80%, rgba(6, 182, 212, 0.1) 0%, transparent 50%)',
          pointerEvents: 'none',
          zIndex: 0,
      },
    }}>
      <AppBar position="sticky" elevation={0}>
        <Toolbar>
          <Box sx={{ flexGrow: 1, display: 'flex', alignItems: 'baseline', gap: 2 }}>
            <Typography 
              variant="h5" 
              component="h1" 
              sx={{ 
                fontWeight: 700,
                background: 'linear-gradient(135deg, #00d4ff 0%, #00ff88 100%)',
                backgroundClip: 'text',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
              }}
            >
              ONE UI
            </Typography>
            <Typography 
              variant="body2" 
              sx={{ 
                opacity: 0.7,
                color: '#a0aec0',
              }}
            >
              {tools.length} tools available
            </Typography>
          </Box>
          
          {/* Show Admin button only for admins */}
          {user && isAdminRole(user.role_name) && (
            <Button
              variant="outlined"
              startIcon={<Settings />}
              onClick={() => setShowAdminPage(true)}
              sx={{ 
                mr: 2,
                borderColor: 'rgba(0, 212, 255, 0.5)',
                color: '#00d4ff',
                fontWeight: 600,
                '&:hover': {
                  borderColor: '#00d4ff',
                  backgroundColor: 'rgba(0, 212, 255, 0.1)',
                },
              }}
            >
              Admin
            </Button>
          )}
          
          {/* User menu */}
          <IconButton onClick={handleMenuOpen} color="inherit">
            <AccountCircle />
          </IconButton>
          <Menu
            anchorEl={anchorEl}
            open={Boolean(anchorEl)}
            onClose={handleMenuClose}
          >
            <MenuItem disabled>
              <Typography variant="body2">
                {user?.first_name} {user?.last_name}
              </Typography>
            </MenuItem>
            <MenuItem disabled>
              <Typography variant="caption" color="text.secondary">
                {user?.email}
              </Typography>
            </MenuItem>
            <MenuItem disabled>
              <Chip label={user?.role_name} size="small" color="primary" />
            </MenuItem>
            <MenuItem onClick={handleLogout}>
              <Logout fontSize="small" sx={{ mr: 1 }} />
              Logout
            </MenuItem>
          </Menu>
        </Toolbar>
        <Container maxWidth="xl" sx={{ pb: 2 }}>
          <Stack direction="row" spacing={2} alignItems="center" flexWrap="wrap">
            {/* Filter Dropdown */}
            <Box sx={{ minWidth: 220, maxWidth: 250 }}>
              <FilterSidebar
                tags={allTags}
                selectedTags={selectedTags}
                onTagToggle={handleTagToggle}
              />
            </Box>
            
            {/* Search Bar */}
            <Box sx={{ flexGrow: 1, minWidth: 300 }}>
              <SearchBar value={searchQuery} onChange={handleSearchChange} />
            </Box>
            
            {/* AI Search Button */}
            <Button
              variant="contained"
              startIcon={<Psychology />}
              onClick={handleAISearch}
              disabled={aiLoading}
              sx={{ 
                minWidth: 120,
                background: 'linear-gradient(135deg, #00d4ff 0%, #00ff88 100%)',
                color: '#0a0e27',
                fontWeight: 600,
              }}
            >
              {aiLoading ? 'Searching...' : 'AI Search'}
            </Button>
          </Stack>
        </Container>
      </AppBar>

      <Container maxWidth="xl" sx={{ flexGrow: 1, py: 4 }}>
        <Box sx={{ display: 'flex', gap: 3 }}>
          {/* Tools Grid */}
          <Box sx={{ flexGrow: 1 }}>
            {loading ? (
              <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: 400 }}>
                <CircularProgress 
                  size={60} 
                  sx={{
                    color: '#00ff88',
                    '& .MuiCircularProgress-circle': {
                      strokeLinecap: 'round',
                    },
                  }}
                />
              </Box>
            ) : error ? (
              <Box sx={{ textAlign: 'center', py: 8 }}>
                <Alert 
                  severity="error" 
                  sx={{ 
                    mb: 2,
                    backgroundColor: 'rgba(255, 0, 0, 0.1)',
                    border: '1px solid rgba(255, 0, 0, 0.3)',
                    color: '#ff6b6b',
                  }}
                >
                  {error}
                </Alert>
                <Button variant="contained" onClick={loadData}>
                  Retry
                </Button>
              </Box>
            ) : filteredTools.length === 0 ? (
              <Box sx={{ textAlign: 'center', py: 8 }}>
                <SearchOff sx={{ fontSize: 64, color: '#10b981', mb: 2, opacity: 0.5 }} />
                <Typography variant="h6" gutterBottom sx={{ color: '#10b981' }}>
                  No tools found
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  {searchQuery || selectedTags.length > 0
                    ? 'Try adjusting your search or filters'
                    : 'No tools available yet'}
                </Typography>
              </Box>
            ) : (
              <Box 
                sx={{ 
                  display: 'grid', 
                  gridTemplateColumns: {
                    xs: '1fr',
                    sm: 'repeat(2, 1fr)',
                    md: 'repeat(3, 1fr)',
                  },
                  gap: 3,
                }}
              >
                {filteredTools.map((tool) => (
                  <ToolCard key={tool.id} tool={tool} />
                ))}
              </Box>
            )}
          </Box>
        </Box>
      </Container>
    </Box>
    </>
  );
}

export default App;
