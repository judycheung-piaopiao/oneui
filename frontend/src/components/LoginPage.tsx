import { Box, Container, Typography, Paper, Button } from '@mui/material';
import { Google } from '@mui/icons-material';

interface LoginPageProps {
  onLoginSuccess: (token: string) => void;
}

export default function LoginPage(_props: LoginPageProps) {
  const handleGoogleLogin = () => {
    // Direct redirect to our own backend Google OAuth endpoint
    const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8889';
    window.location.href = `${apiBaseUrl}/auth/google/login`;
  };

  return (
    <Box
      sx={{
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        background: 'linear-gradient(135deg, #0a0e27 0%, #1a1f3a 100%)',
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
            backgroundColor: 'rgba(10, 14, 39, 0.8)',
            backdropFilter: 'blur(10px)',
            border: '1px solid rgba(0, 212, 255, 0.2)',
          }}
        >
          <Typography 
            variant="h4" 
            component="h1" 
            gutterBottom
            sx={{
              background: 'linear-gradient(135deg, #00d4ff 0%, #00ff88 100%)',
              backgroundClip: 'text',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
              fontWeight: 700,
            }}
          >
            ONE UI
          </Typography>
          <Typography variant="body1" sx={{ color: 'rgba(255, 255, 255, 0.7)' }} align="center">
            Please sign in with your company Google account
          </Typography>

          <Button
            variant="contained"
            startIcon={<Google />}
            onClick={handleGoogleLogin}
            sx={{
              mt: 2,
              py: 1.5,
              px: 4,
              background: 'linear-gradient(135deg, #00d4ff 0%, #00ff88 100%)',
              color: '#0a0e27',
              fontWeight: 600,
              fontSize: '1rem',
              '&:hover': {
                boxShadow: '0 6px 25px rgba(0, 212, 255, 0.6)',
                transform: 'translateY(-2px)',
              },
            }}
          >
            Sign in with Google
          </Button>
        </Paper>
      </Container>
    </Box>
  );
}
