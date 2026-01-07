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
import { Settings, SearchOff, AccountCircle, Logout, Psychology } from '@mui/icons-material';
import ToolCard from './ToolCard';
import SearchBar from './SearchBar';
import FilterSidebar from './FilterSidebar';
import AdminPage from './AdminPage';
import ParticlesBackground from './ParticlesBackground';
import type { Tool } from '../types';
import { getTools, getAllTags, aiSearch, docSearch, checkIsAdmin } from '../api/tools';
import '../App.css';

// MainApp component that receives user and auth from GuardedRoute
function MainApp({ user, auth }: any) {
  // Hardcoded admin emails - add your email here
  const ADMIN_EMAILS = [
    'jun.zhang@alpha-grep.com',
    // Add more admin emails here as needed
  ];

  const [tools, setTools] = useState<Tool[]>([]);
  const [filteredTools, setFilteredTools] = useState<Tool[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [allTags, setAllTags] = useState<string[]>([]);
  const [selectedTags, setSelectedTags] = useState<string[]>([]);
  const [showAdminPage, setShowAdminPage] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const [aiLoading, setAiLoading] = useState(false);
  const [isAIResult, setIsAIResult] = useState(false);
  const [isAdmin, setIsAdmin] = useState(false);

  const loadData = async () => {
    try {
      setLoading(true);
      const [toolsData, tagsData, adminStatus] = await Promise.all([
        getTools(),
        getAllTags(),
        checkIsAdmin(),
      ]);
      setTools(toolsData);
      setAllTags(tagsData);
      
      // Check admin permission based on VITE_DEV_MODE
      const isDevMode = import.meta.env.VITE_DEV_MODE === 'true';
      const isHardcodedAdmin = ADMIN_EMAILS.includes(user?.email || '');
      
      // In dev mode, everyone is admin; otherwise check hardcoded list or backend
      setIsAdmin(isDevMode || isHardcodedAdmin || adminStatus);
    } catch (error) {
      console.error('Failed to load data:', error);
      setError('Failed to load tools. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const filterTools = () => {
    let filtered = [...tools];

    if (searchQuery) {
      const query = searchQuery.toLowerCase().trim();
      
      const scoredResults = tools.map((tool) => {
        const name = tool.name.toLowerCase();
        const description = tool.description.toLowerCase();
        const tags = tool.tags.map(t => t.toLowerCase());
        
        let score = 0;
        
        if (name === query) score = 1000;
        else if (name.startsWith(query)) score = 900;
        else if (name.includes(query)) score = 800;
        else if (name.split(/[\s-_]+/).some(word => word.startsWith(query))) score = 700;
        else if (tags.some(tag => tag.includes(query) || tag.startsWith(query))) score = 500;
        else if (description.includes(query)) score = 300;
        else if (description.split(/[\s-_]+/).some(word => word.startsWith(query))) score = 200;
        
        return { tool, score };
      }).filter(item => item.score > 0);
      
      filtered = scoredResults
        .sort((a, b) => b.score - a.score)
        .map(item => item.tool);
    }

    if (selectedTags.length > 0) {
      filtered = filtered.filter((tool) =>
        selectedTags.some((tag) => tool.tags.includes(tag))
      );
    }

    if (!searchQuery) {
      const priorityOrder = ['ag trades db', 'ag cms', 'periscope'];
      filtered.sort((a, b) => {
        const aName = a.name.toLowerCase();
        const bName = b.name.toLowerCase();
        const aIndex = priorityOrder.indexOf(aName);
        const bIndex = priorityOrder.indexOf(bName);
        
        if (aIndex !== -1 && bIndex !== -1) return aIndex - bIndex;
        if (aIndex !== -1) return -1;
        if (bIndex !== -1) return 1;
        return 0;
      });
    }

    setFilteredTools(filtered);
  };

  const handleAISearch = async () => {
    if (!searchQuery.trim()) {
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
      const [aiResponse, docResponse] = await Promise.all([
        aiSearch(searchQuery, 20),
        docSearch(searchQuery, 20)
      ]);
      
      const aiResults = aiResponse.results.map((r: any) => ({
        id: r.id,
        name: r.name,
        description: r.description,
        icon: r.icon,
        tool_link: r.tool_link,
        documentation_link: r.documentation_link,
        tags: r.tags,
      }));
      
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
      
      const aiToolIds = new Set(aiResults.map((t: Tool) => t.id));
      const docToolIds = new Set(docResults.map((d: any) => d.id));
      
      const bothResults = aiResults.filter((t: Tool) => docToolIds.has(t.id));
      const aiOnlyResults = aiResults.filter((t: Tool) => !docToolIds.has(t.id));
      const docOnlyResults = tools.filter(t => docToolIds.has(t.id) && !aiToolIds.has(t.id));
      
      const mergedResults = [
        ...bothResults,
        ...aiOnlyResults,
        ...docOnlyResults.slice(0, 10 - bothResults.length - aiOnlyResults.length)
      ];
      
      setFilteredTools(mergedResults);
      setIsAIResult(true);
    } catch (error) {
      console.error('AI search failed:', error);
      filterTools();
    } finally {
      setAiLoading(false);
    }
  };

  useEffect(() => {
    if (isAIResult) {
      handleAISearch();
    } else {
      filterTools();
    }
  }, [tools, searchQuery, selectedTags]);

  const handleSearchChange = (value: string) => {
    setSearchQuery(value);
    setIsAIResult(false);
  };

  const handleTagToggle = (tag: string) => {
    setSelectedTags((prev) =>
      prev.includes(tag) ? prev.filter((t) => t !== tag) : [...prev, tag]
    );
    setIsAIResult(false);
  };

  const handleLogout = () => {
    auth.logout();
    window.location.href = '/login';
  };

  const handleMenuOpen = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
  };

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
            
            {isAdmin && (
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
            
            <IconButton onClick={handleMenuOpen} color="inherit">
              <AccountCircle />
            </IconButton>
            <Menu
              anchorEl={anchorEl}
              open={Boolean(anchorEl)}
              onClose={handleMenuClose}
              PaperProps={{
                sx: {
                  mt: 1.5,
                  backgroundColor: 'rgba(10, 14, 39, 0.95)',
                  backdropFilter: 'blur(10px)',
                  border: '1px solid rgba(0, 212, 255, 0.2)',
                  minWidth: 220,
                },
              }}
            >
              <MenuItem disabled sx={{ opacity: 1 }}>
                <Typography variant="body2" sx={{ fontWeight: 600, color: '#fff' }}>
                  {user?.first_name || user?.firstName} {user?.last_name || user?.lastName}
                </Typography>
              </MenuItem>
              <MenuItem disabled sx={{ opacity: 1 }}>
                <Typography variant="caption" sx={{ color: 'rgba(255, 255, 255, 0.7)' }}>
                  {user?.email}
                </Typography>
              </MenuItem>
              <MenuItem disabled sx={{ opacity: 1, py: 1 }}>
                <Chip 
                  label={user?.role_name || user?.role} 
                  size="small" 
                  sx={{ 
                    backgroundColor: 'rgba(0, 212, 255, 0.2)',
                    color: '#00d4ff',
                    border: '1px solid rgba(0, 212, 255, 0.4)',
                    fontWeight: 600,
                  }}
                />
              </MenuItem>
              <MenuItem 
                onClick={handleLogout}
                sx={{
                  mt: 1,
                  borderTop: '1px solid rgba(255, 255, 255, 0.1)',
                  '&:hover': {
                    backgroundColor: 'rgba(0, 212, 255, 0.1)',
                  },
                }}
              >
                <Logout fontSize="small" sx={{ mr: 1, color: '#00d4ff' }} />
                <Typography sx={{ color: '#fff' }}>Logout</Typography>
              </MenuItem>
            </Menu>
          </Toolbar>
          <Container maxWidth="xl" sx={{ pb: 2 }}>
            <Stack direction="row" spacing={2} alignItems="center" flexWrap="wrap">
              <Box sx={{ minWidth: 220, maxWidth: 250 }}>
                <FilterSidebar
                  tags={allTags}
                  selectedTags={selectedTags}
                  onTagToggle={handleTagToggle}
                />
              </Box>
              
              <Box sx={{ flexGrow: 1, minWidth: 300 }}>
                <SearchBar value={searchQuery} onChange={handleSearchChange} />
              </Box>
              
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

export default MainApp;
