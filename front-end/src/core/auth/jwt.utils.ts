import { DecodedToken } from '@core/auth/auth.types';


export const decodeToken = (token: string): DecodedToken | null => {
  try {
    const parts = token.split('.');
    if (parts.length !== 3) return null;
    
    // Decode base64 URL format safely
    const payload = parts[1].replace(/-/g, '+').replace(/_/g, '/');
    const jsonPayload = decodeURIComponent(
      window
        .atob(payload)
        .split('')
        .map((c) => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2))
        .join('')
    );

    return JSON.parse(jsonPayload) as DecodedToken;
  } catch (error) {
    console.error('Failed to decode JWT token:', error);
    return null;
  }
};

export const extractRoleFromToken = (decoded: DecodedToken): string => {
  if (!decoded) return 'Parent';
  const roleVal = decoded.role || decoded['http://schemas.microsoft.com/ws/2008/06/identity/claims/role'];
  if (!roleVal) return 'Parent';
  if (Array.isArray(roleVal)) {
    return roleVal[0] || 'Parent';
  }
  return roleVal;
};

export const extractUserIdFromToken = (decoded: DecodedToken): string => {
  if (!decoded) return '';
  return decoded.sub || decoded['http://schemas.xmlsoap.org/ws/2005/05/identity/claims/nameidentifier'] || '';
};

export const extractEmailFromToken = (decoded: DecodedToken): string => {
  if (!decoded) return '';
  return decoded.email || decoded['http://schemas.xmlsoap.org/ws/2005/05/identity/claims/emailaddress'] || '';
};
