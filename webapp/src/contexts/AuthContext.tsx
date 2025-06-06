import React, { createContext, useEffect, useState } from 'react';
import type { ReactNode } from 'react';
import { authService } from '../services/authService';
import type { User } from '../services/authService';

interface AuthContextType {
  user: User | null;
  loading: boolean;
  isAuthenticated: boolean;
  signIn: (username: string, password: string) => Promise<void>;
  signUp: (email: string, password: string) => Promise<void>;
  confirmSignUp: (username: string, confirmationCode: string) => Promise<void>;
  signOut: () => Promise<void>;
  refreshUser: () => Promise<void>;
}

export type { AuthContextType };

export const AuthContext = createContext<AuthContextType | undefined>(undefined);

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  // 初期化時にユーザー情報を取得
  useEffect(() => {
    initializeAuth();
  }, []);

  const initializeAuth = async () => {
    try {
      console.log('🔍 Auth initialization started...');
      const hasTokens = authService.isAuthenticated();
      console.log('📋 Has tokens in localStorage:', hasTokens);
      
      if (hasTokens) {
        const accessToken = authService.getAccessToken();
        console.log('🎫 Access token found:', accessToken?.substring(0, 20) + '...');
        
        console.log('👤 Getting current user...');
        const currentUser = await authService.getCurrentUser();
        console.log('✅ Current user result:', currentUser);
        setUser(currentUser);
      } else {
        console.log('❌ No tokens found - user not authenticated');
        setUser(null);
      }
    } catch (error) {
      console.error('❌ Auth initialization error:', error);
      setUser(null);
    } finally {
      setLoading(false);
      console.log('🎯 Auth initialization completed. User:', user);
    }
  };

  const signIn = async (username: string, password: string) => {
    try {
      await authService.signIn(username, password);
      await refreshUser();
    } catch (error) {
      console.error('Sign in error:', error);
      throw error;
    }
  };

  const signUp = async (email: string, password: string) => {
    try {
      await authService.signUp(email, password);
    } catch (error) {
      console.error('Sign up error:', error);
      throw error;
    }
  };

  const confirmSignUp = async (username: string, confirmationCode: string) => {
    try {
      await authService.confirmSignUp(username, confirmationCode);
    } catch (error) {
      console.error('Confirm sign up error:', error);
      throw error;
    }
  };

  const signOut = async () => {
    try {
      await authService.signOut();
      setUser(null);
    } catch (error) {
      console.error('Sign out error:', error);
      throw error;
    }
  };

  const refreshUser = async () => {
    try {
      const currentUser = await authService.getCurrentUser();
      setUser(currentUser);
    } catch (error) {
      console.error('Refresh user error:', error);
      setUser(null);
    }
  };

  const value: AuthContextType = {
    user,
    loading,
    isAuthenticated: !!user,
    signIn,
    signUp,
    confirmSignUp,
    signOut,
    refreshUser,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};
