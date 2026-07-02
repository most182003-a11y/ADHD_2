export interface DecodedToken {
  sub?: string;
  email?: string;
  unique_name?: string;
  role?: string | string[];
  exp?: number;
  // ASP.NET Core Identity Claim URIs
  'http://schemas.xmlsoap.org/ws/2005/05/identity/claims/nameidentifier'?: string;
  'http://schemas.xmlsoap.org/ws/2005/05/identity/claims/emailaddress'?: string;
  'http://schemas.microsoft.com/ws/2008/06/identity/claims/role'?: string | string[];
}

export type Role = 'Admin' | 'Doctor' | 'Parent';

export interface AuthState {
  token: string | null;
  role: Role | null;
  isAuthenticated: boolean;
  login: (token: string, role: Role) => void;
  logout: () => void;
}
