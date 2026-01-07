declare module 'ag-ui-components' {
  import { ComponentType } from 'react';

  export class AuthService {
    constructor(
      cookieName: string,
      authUrl?: string,
      validateUrl?: string,
      googleAuthUrl?: string
    );
    logout(): void;
    getCookie(name: string): string | null;
    setCookie(name: string, value: string): void;
    removeCookie(name: string): void;
  }

  export interface LoginProps {
    authUrl?: string;
    cookieName: string;
    validateUrl: string;
    googleAuthUrl?: string;
    auth: AuthService;
    isNativeLoginEnabled?: boolean;
    hasGoogleLogin?: boolean;
    defaultRoute?: string;
  }

  export interface GuardedRouteProps {
    path: string;
    component: ComponentType<any>;
    authUrl?: string;
    cookieName: string;
    validateUrl: string;
    googleAuthUrl?: string;
    auth: AuthService;
    token?: string | null;
  }

  export const Login: ComponentType<LoginProps>;
  export const GuardedRoute: ComponentType<GuardedRouteProps>;
  
  // Other exports from ag-ui-components
  export const SimpleForm: ComponentType<any>;
  export const StyledForm: ComponentType<any>;
  export const GLogout: ComponentType<any>;
  export const ProfileManagerComponent: ComponentType<any>;
  export const ConnectionIndicator: ComponentType<any>;
  export function getProfileDirectoryAPI(...args: any[]): any;
}
