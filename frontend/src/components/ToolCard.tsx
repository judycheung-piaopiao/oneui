import { Card, CardContent, CardActions, Typography, Chip, Button, Box, Stack } from '@mui/material';
import { OpenInNew, MenuBook } from '@mui/icons-material';
import type { Tool } from '../types';

interface ToolCardProps {
  tool: Tool;
}

export default function ToolCard({ tool }: ToolCardProps) {
  const getIconDisplay = (icon?: string) => {
    if (!icon) return { content: '🔧', isImage: false };
    if (icon.length <= 2) return { content: icon, isImage: false };
    if (icon.startsWith('http') || icon.startsWith('/')) {
      return { 
        content: <img src={icon} alt={tool.name} style={{ width: 48, height: 48, objectFit: 'contain' }} />,
        isImage: true 
      };
    }
    return { content: icon, isImage: false };
  };

  // Get token and append to tool link for SSO
  const getToolLinkWithToken = (link: string) => {
    // ag-ui-components stores token in cookie with name 'ag_token'
    const getCookie = (name: string) => {
      const value = `; ${document.cookie}`;
      const parts = value.split(`; ${name}=`);
      if (parts.length === 2) return parts.pop()?.split(';').shift();
      return null;
    };
    
    const token = getCookie('ag_token') || localStorage.getItem('ag_token') || localStorage.getItem('access_token');
    if (!token) return link;
    
    try {
      const url = new URL(link);
      url.searchParams.set('ag-token', token);
      return url.toString();
    } catch {
      // If URL parsing fails, return original link
      return link;
    }
  };

  const iconInfo = getIconDisplay(tool.icon);

  return (
    <Card 
      sx={{ 
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
        position: 'relative',
        overflow: 'hidden',
        background: 'rgba(255, 255, 255, 0.05)',
        backdropFilter: 'blur(10px)',
        border: '1px solid rgba(255, 255, 255, 0.1)',
        transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
        '&::before': {
          content: '""',
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          height: '3px',
          background: 'linear-gradient(90deg, #00d4ff, #00ff88, #00d4ff)',
          opacity: 0,
          transition: 'opacity 0.3s ease',
        },
        '&:hover': {
          transform: 'translateY(-4px)',
          boxShadow: '0 8px 32px rgba(0, 212, 255, 0.15), 0 0 0 1px rgba(0, 212, 255, 0.3)',
          background: 'rgba(255, 255, 255, 0.08)',
        },
        '&:hover::before': {
          opacity: 1,
        },
      }}
    >
      <CardContent sx={{ flexGrow: 1 }}>
        <Stack direction="row" spacing={2} alignItems="center" mb={2}>
          <Box 
            sx={{ 
              fontSize: '2rem',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              width: 56,
              height: 56,
              transition: 'all 0.3s ease',
              '&:hover': {
                transform: 'scale(1.1)',
              },
            }}
          >
            {iconInfo.content}
          </Box>
          <Typography 
            variant="h6" 
            component="h3" 
            sx={{ 
              flexGrow: 1, 
              fontWeight: 600,
              background: 'linear-gradient(135deg, #ffffff 0%, #10b981 100%)',
              backgroundClip: 'text',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
            }}
          >
            {tool.name}
          </Typography>
        </Stack>

        <Typography 
          variant="body2" 
          color="text.secondary" 
          sx={{ 
            mb: 2,
            overflow: 'hidden',
            textOverflow: 'ellipsis',
            display: '-webkit-box',
            WebkitLineClamp: 3,
            WebkitBoxOrient: 'vertical',
            minHeight: '3.6em',
          }}
        >
          {tool.description}
        </Typography>

        {tool.doc_match && (
          <Chip 
            label={`Matched in docs (${(tool.doc_match.relevance_score * 100).toFixed(0)}% relevant)`}
            size="small"
            sx={{
              mt: 1,
              mb: 1,
              backgroundColor: 'rgba(0, 212, 255, 0.15)',
              color: '#00d4ff',
              border: '1px solid rgba(0, 212, 255, 0.4)',
              fontWeight: 600,
              boxShadow: '0 0 10px rgba(0, 212, 255, 0.2)',
              transition: 'all 0.3s ease',
              '&:hover': {
                boxShadow: '0 0 15px rgba(0, 212, 255, 0.4)',
              },
            }}
          />
        )}

        {tool.tags && tool.tags.length > 0 && (
          <Stack direction="row" spacing={1} flexWrap="wrap" gap={1}>
            {tool.tags.map((tag) => (
              <Chip 
                key={tag} 
                label={tag} 
                size="small"
                sx={{
                  backgroundColor: 'rgba(0, 255, 136, 0.1)',
                  color: '#00ff88',
                  border: '1px solid rgba(0, 255, 136, 0.4)',
                  fontWeight: 600,
                  transition: 'all 0.3s ease',
                  '&:hover': {
                    backgroundColor: 'rgba(0, 255, 136, 0.2)',
                    boxShadow: '0 0 10px rgba(0, 255, 136, 0.3)',
                    transform: 'scale(1.05)',
                  },
                }}
              />              
            ))}
          </Stack>
        )}
      </CardContent>

      <CardActions sx={{ p: 2, pt: 0, gap: 1 }}>
        <Button
          variant="contained"
          startIcon={<OpenInNew />}
          href={getToolLinkWithToken(tool.tool_link)}
          target="_blank"
          rel="noopener noreferrer"
          sx={{
            flex: 1,
            background: 'linear-gradient(135deg, #00d4ff 0%, #00ff88 100%)',
            color: '#0a0e27',
            fontWeight: 700,
            boxShadow: '0 4px 15px rgba(0, 212, 255, 0.3)',
            transition: 'all 0.3s ease',
            '&:hover': {
              background: 'linear-gradient(135deg, #00ff88 0%, #00d4ff 100%)',
              boxShadow: '0 6px 25px rgba(0, 212, 255, 0.6), 0 0 20px rgba(0, 255, 136, 0.4)',
              transform: 'translateY(-2px)',
            },
          }}
        >
          Tool
        </Button>
        
        {tool.documentation_link && (
          <Button
            variant="outlined"
            startIcon={<MenuBook />}
            href={tool.documentation_link}
            target="_blank"
            rel="noopener noreferrer"
            sx={{ 
              flex: 1,
              borderColor: 'rgba(0, 212, 255, 0.6)',
              borderWidth: 2,
              color: '#00d4ff',
              fontWeight: 600,
              transition: 'all 0.3s ease',
              '&:hover': {
                borderColor: '#00ff88',
                backgroundColor: 'rgba(0, 212, 255, 0.1)',
                boxShadow: '0 0 20px rgba(0, 212, 255, 0.5)',
                color: '#00ff88',
              },
            }}
          >
            Docs
          </Button>
        )}
      </CardActions>
    </Card>
  );
}
