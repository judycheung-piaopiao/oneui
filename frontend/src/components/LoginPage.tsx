import { Box, Container, Typography, Paper } from '@mui/material';
import { useEffect } from 'react';

interface LoginPageProps {
  onLoginSuccess: (token: string) => void;
}

export default function LoginPage({ onLoginSuccess }: LoginPageProps) {
  useEffect(() => {
    const handleMessage = (event: MessageEvent) => {
      const data = event.data || {};
      
      // Handle Google login response
      if (data.type === 'googleLogin' && data.token) {
        localStorage.setItem('access_token', data.token);
        onLoginSuccess(data.token);
      }
      
      // Handle regular login response
      if (data.access_token) {
        localStorage.setItem('access_token', data.access_token);
        onLoginSuccess(data.access_token);
      }
    };

    window.addEventListener('message', handleMessage);
    return () => window.removeEventListener('message', handleMessage);
  }, [onLoginSuccess]);

  const googleLoginUrl = 'https://microfrontends.alpha-grep.com/googlelogin';

  return (
    <Box
      sx={{
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        bgcolor: 'background.default',
      }}
    >
      <Container maxWidth="sm">
        <Paper
          elevation={3}
          sx={{
            p: 4,
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            gap: 3,
          }}
        >
          <Typography variant="h4" component="h1" gutterBottom>
            AG Tools Catalogue
          </Typography>
          <Typography variant="body1" color="text.secondary" align="center">
            Please sign in with your company Google account
          </Typography>

          <Box
            sx={{
              width: '100%',
              display: 'flex',
              justifyContent: 'center',
            }}
          >
            <iframe
              src={googleLoginUrl}
              style={{
                border: 'none',
                width: '100%',
                height: '60px',
                overflow: 'hidden',
              }}
              title="Google Login"
            />
          </Box>
        </Paper>
      </Container>
    </Box>
  );
}
