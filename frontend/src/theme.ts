import { createTheme } from '@mui/material/styles';

export const darkTheme = createTheme({
  palette: {
    mode: 'dark',
    primary: {
      main: '#10b981', // Emerald green
      light: '#34d399',
      dark: '#059669',
    },
    secondary: {
      main: '#06b6d4', // Sky blue
      light: '#22d3ee',
      dark: '#0891b2',
    },
    background: {
      default: '#0a0e27', // Deep dark blue-black
      paper: 'rgba(26, 31, 58, 0.7)', // Semi-transparent for glassmorphism
    },
    text: {
      primary: '#ffffff',
      secondary: '#a0aec0',
    },
    divider: 'rgba(16, 185, 129, 0.12)',
  },
  typography: {
    fontFamily: '"Inter", system-ui, -apple-system, sans-serif',
    h5: {
      fontWeight: 700,
      letterSpacing: '-0.5px',
    },
  },
  components: {
    MuiCssBaseline: {
      styleOverrides: {
        body: {
          background: 'linear-gradient(135deg, #0a0e27 0%, #1a1f3a 100%)',
          backgroundAttachment: 'fixed',
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          backgroundImage: 'none',
          backgroundColor: 'rgba(26, 31, 58, 0.5)',
          backdropFilter: 'blur(10px)',
          borderRadius: 16,
          border: '1px solid rgba(255, 255, 255, 0.05)',
          transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
          '&:hover': {
            transform: 'translateY(-4px)',
            boxShadow: '0 0 30px rgba(16, 185, 129, 0.3)',
            borderColor: 'rgba(16, 185, 129, 0.3)',
          },
        },
      },
    },
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: 10,
          textTransform: 'none',
          fontWeight: 600,
          transition: 'all 0.3s ease',
        },
        contained: {
          background: 'linear-gradient(135deg, #10b981 0%, #06b6d4 100%)',
          boxShadow: '0 4px 20px rgba(16, 185, 129, 0.4)',
          '&:hover': {
            background: 'linear-gradient(135deg, #10b981 0%, #06b6d4 100%)',
            boxShadow: '0 6px 30px rgba(16, 185, 129, 0.6)',
            transform: 'translateY(-2px)',
          },
        },
        outlined: {
          borderColor: 'rgba(16, 185, 129, 0.5)',
          color: '#10b981',
          '&:hover': {
            borderColor: '#10b981',
            backgroundColor: 'rgba(16, 185, 129, 0.1)',
            boxShadow: '0 0 20px rgba(16, 185, 129, 0.2)',
          },
        },
      },
    },
    MuiChip: {
      styleOverrides: {
        root: {
          borderRadius: 8,
          fontWeight: 500,
        },
        filled: {
          backgroundColor: 'rgba(16, 185, 129, 0.15)',
          color: '#10b981',
          border: '1px solid rgba(16, 185, 129, 0.3)',
        },
      },
    },
    MuiPaper: {
      styleOverrides: {
        root: {
          backgroundImage: 'none',
          backgroundColor: 'rgba(26, 31, 58, 0.6)',
          backdropFilter: 'blur(10px)',
          border: '1px solid rgba(255, 255, 255, 0.05)',
        },
      },
    },
    MuiAppBar: {
      styleOverrides: {
        root: {
          backgroundColor: 'rgba(10, 14, 39, 0.8)',
          backdropFilter: 'blur(20px)',
          borderBottom: '1px solid rgba(16, 185, 129, 0.1)',
        },
      },
    },
  },
});
