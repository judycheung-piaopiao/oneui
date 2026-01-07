import { Suspense } from 'react';
import { BrowserRouter as Router, Switch, Route } from 'react-router-dom';
import { Login, GuardedRoute, AuthService } from 'ag-ui-components';
import 'ag-ui-components/dist/index.css';
import { CircularProgress, Box } from '@mui/material';
import MainApp from './components/MainApp';

const TOKEN_KEY = 'ag_token';
const AUTH_URL = import.meta.env.VITE_AUTH_URL;
const VALIDATE_URL = import.meta.env.VITE_VALIDATE_URL || 'https://access-service.alpha-grep.com/user/verifyAccessToken';
const GOOGLE_AUTH_URL = import.meta.env.VITE_GOOGLE_AUTH_URL || 'https://access-service.alpha-grep.com/user/validateGoogleUser';

const GUARDED_ROUTE_PROPS = {
  authUrl: AUTH_URL,
  cookieName: TOKEN_KEY,
  validateUrl: VALIDATE_URL,
  googleAuthUrl: GOOGLE_AUTH_URL,
  auth: new AuthService(TOKEN_KEY, AUTH_URL, VALIDATE_URL, GOOGLE_AUTH_URL),
};

function App() {
  const userToken = new URLSearchParams(window.location.search).get('ag-token');

  return (
    <Suspense
      fallback={
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
      }
    >
      <Router>
        <Switch>
          <Route
            exact
            path="/login"
            component={() => (
              <Login
                {...GUARDED_ROUTE_PROPS}
                isNativeLoginEnabled={false}
                hasGoogleLogin={true}
                defaultRoute="/"
              />
            )}
          />
          <GuardedRoute
            path="/"
            component={MainApp}
            {...GUARDED_ROUTE_PROPS}
            token={userToken}
          />
        </Switch>
      </Router>
    </Suspense>
  );
}

export default App;
