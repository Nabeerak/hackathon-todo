// T036: Implement signout functionality with session cleanup
// T093: Add responsive navigation header
// Blood Red & Yellow Theme Header

"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { apiClient, TokenManager } from "@/lib/api";
import { AuthService, type AuthState } from "@/lib/auth";

export default function Header() {
  const [isSigningOut, setIsSigningOut] = useState(false);
  const [authState, setAuthState] = useState<AuthState>({
    isAuthenticated: false,
    userId: null,
    userEmail: null,
  });

  // Check auth state only on client side to avoid hydration mismatch
  useEffect(() => {
    setAuthState(AuthService.getAuthState());
  }, []);

  const handleSignout = async () => {
    if (isSigningOut) return;

    setIsSigningOut(true);
    try {
      await apiClient.signout();
      TokenManager.removeToken();
      window.location.href = "/auth/signin";
    } catch (error) {
      console.error("Signout error:", error);
      // Force signout even if API call fails
      TokenManager.removeToken();
      window.location.href = "/auth/signin";
    }
  };

  return (
    <header
      className="fixed top-0 w-full z-50"
      style={{
        height: '70px',
        background: 'rgba(15, 15, 15, 0.4)',
        borderBottom: '1px solid rgba(139, 0, 0, 0.3)',
        backdropFilter: 'blur(20px)',
      }}
    >
      <div style={{ maxWidth: '100%', height: '100%', width: '100%', paddingLeft: '64px', paddingRight: '64px' }}>
        <div className="flex items-center justify-between h-full">
          {/* Logo */}
          <Link href={authState.isAuthenticated ? "/tasks" : "/"} className="flex items-center gap-2">
            <div
              className="flex items-center justify-center"
              style={{ color: '#8B0000', width: '16px', height: '16px' }}
            >
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
                <path d="M20 6L9 17L4 12" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round"/>
              </svg>
            </div>
            <span
              style={{
                fontFamily: 'var(--font-inter)',
                fontWeight: '600',
                fontSize: '1.125rem',
                color: '#FFFFFF'
              }}
            >
              Todo <span style={{ color: '#8B0000' }}>App</span>
            </span>
          </Link>

          {/* Auth Buttons */}
          <div className="flex items-center gap-4">
            {authState.isAuthenticated ? (
              <>
                <span className="text-sm hidden sm:inline" style={{ color: '#B0B0B0' }}>
                  {authState.userEmail}
                </span>
                <button
                  onClick={handleSignout}
                  disabled={isSigningOut}
                  className="transition-all duration-200"
                  style={{
                    fontFamily: 'var(--font-inter)',
                    fontWeight: '600',
                    fontSize: '0.9375rem',
                    background: '#8B0000',
                    color: '#FFFFFF',
                    padding: '10px 24px',
                    borderRadius: '6px',
                    border: 'none',
                    cursor: isSigningOut ? 'not-allowed' : 'pointer',
                  }}
                  onMouseEnter={(e) => {
                    if (!isSigningOut) e.currentTarget.style.background = '#A01010';
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.background = '#8B0000';
                  }}
                >
                  {isSigningOut ? "Signing out..." : "Sign Out"}
                </button>
              </>
            ) : (
              <>
                <Link
                  href="/auth/signin"
                  className="hidden sm:inline-block transition-colors duration-200"
                  style={{
                    fontFamily: 'var(--font-inter)',
                    fontWeight: '500',
                    fontSize: '0.9375rem',
                    color: '#B0B0B0',
                    textDecoration: 'none',
                  }}
                  onMouseEnter={(e) => e.currentTarget.style.color = '#FFFFFF'}
                  onMouseLeave={(e) => e.currentTarget.style.color = '#B0B0B0'}
                >
                  Sign In
                </Link>
                <Link
                  href="/auth/signup"
                  className="transition-all duration-200"
                  style={{
                    fontFamily: 'var(--font-inter)',
                    fontWeight: '600',
                    fontSize: '0.9375rem',
                    background: '#8B0000',
                    color: '#FFFFFF',
                    padding: '10px 24px',
                    borderRadius: '6px',
                    textDecoration: 'none',
                    display: 'inline-block',
                  }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.background = '#A01010';
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.background = '#8B0000';
                  }}
                >
                  Sign Up
                </Link>
              </>
            )}
          </div>
        </div>

      </div>
    </header>
  );
}
