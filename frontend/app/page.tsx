// T029: Create landing page with call-to-action for sign up/sign in
// Blood Red & Yellow Theme Landing Page

"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { AuthService } from "@/lib/auth";
import Header from "@/components/Header";

export default function LandingPage() {
  const router = useRouter();
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  useEffect(() => {
    if (AuthService.isAuthenticated()) {
      setIsAuthenticated(true);
      router.push("/tasks");
    }
  }, [router]);

  if (isAuthenticated) {
    return null;
  }

  return (
    <>
      <Header />
      <main
        style={{
          background: '#0f0f0f',
          minHeight: '100vh',
          paddingTop: '70px',
        }}
      >
        {/* Hero Section - Minimalist */}
        <section
          className="w-full flex items-center justify-center"
          style={{
            minHeight: '550px',
            background: '#0f0f0f',
            padding: '140px 20px 80px',
          }}
        >
          <div className="container mx-auto" style={{ maxWidth: '900px' }}>
            <div className="flex flex-col items-center text-center">
              {/* Main Heading */}
              <h1
                style={{
                  fontFamily: 'var(--font-inter)',
                  fontWeight: '700',
                  fontSize: 'clamp(2.25rem, 5vw, 3.5rem)',
                  color: '#FFFFFF',
                  lineHeight: '1.15',
                  letterSpacing: '-0.02em',
                  maxWidth: '700px',
                  marginBottom: '20px',
                  textAlign: 'center',
                  marginLeft: 'auto',
                  marginRight: 'auto',
                }}
              >
                Organize Your Life with{' '}
                <span
                  style={{
                    position: 'relative',
                    display: 'inline-block',
                  }}
                >
                  <span
                    className="fiery-todo"
                    style={{
                      background: 'linear-gradient(180deg, #FFD700 0%, #FF4500 50%, #DC143C 100%)',
                      WebkitBackgroundClip: 'text',
                      WebkitTextFillColor: 'transparent',
                      backgroundClip: 'text',
                      fontWeight: '800',
                      position: 'relative',
                      zIndex: 2,
                      filter: 'drop-shadow(0 0 10px rgba(255, 69, 0, 0.8)) drop-shadow(0 0 20px rgba(255, 215, 0, 0.6))',
                      animation: 'flicker 1.5s ease-in-out infinite',
                    }}
                  >
                    Todo
                  </span>
                  {/* Top flames with dark smoke */}
                  <span
                    style={{
                      position: 'absolute',
                      top: '-20px',
                      left: '50%',
                      transform: 'translateX(-50%)',
                      width: '100%',
                      height: '40px',
                      background: 'linear-gradient(180deg, rgba(139, 0, 0, 0.9) 0%, rgba(139, 0, 0, 0.6) 50%, transparent 100%)',
                      filter: 'blur(8px) drop-shadow(0 0 12px rgba(0, 0, 0, 0.9)) drop-shadow(0 0 8px rgba(0, 0, 0, 0.7))',
                      animation: 'flameRise 2s ease-in-out infinite',
                      zIndex: 1,
                      pointerEvents: 'none',
                    }}
                  />
                  <span
                    style={{
                      position: 'absolute',
                      top: '-15px',
                      left: '20%',
                      width: '20px',
                      height: '30px',
                      background: 'linear-gradient(180deg, #8B0000 0%, #6B0000 100%)',
                      filter: 'blur(6px) drop-shadow(0 0 10px rgba(0, 0, 0, 0.9)) drop-shadow(0 0 6px rgba(0, 0, 0, 0.8))',
                      animation: 'flame1 1.2s ease-in-out infinite',
                      zIndex: 1,
                      pointerEvents: 'none',
                      borderRadius: '50% 50% 50% 50% / 60% 60% 40% 40%',
                    }}
                  />
                  <span
                    style={{
                      position: 'absolute',
                      top: '-18px',
                      right: '20%',
                      width: '25px',
                      height: '35px',
                      background: 'linear-gradient(180deg, #8B0000 0%, #6B0000 100%)',
                      filter: 'blur(6px) drop-shadow(0 0 10px rgba(0, 0, 0, 0.9)) drop-shadow(0 0 6px rgba(0, 0, 0, 0.8))',
                      animation: 'flame2 1.5s ease-in-out infinite 0.3s',
                      zIndex: 1,
                      pointerEvents: 'none',
                      borderRadius: '50% 50% 50% 50% / 60% 60% 40% 40%',
                    }}
                  />
                  {/* Left side flame */}
                  <span
                    style={{
                      position: 'absolute',
                      top: '20%',
                      left: '-15px',
                      width: '18px',
                      height: '25px',
                      background: 'linear-gradient(90deg, rgba(139, 0, 0, 0.8) 0%, transparent 100%)',
                      filter: 'blur(5px) drop-shadow(0 0 8px rgba(0, 0, 0, 0.9))',
                      animation: 'flameLeft 1.8s ease-in-out infinite',
                      zIndex: 1,
                      pointerEvents: 'none',
                      borderRadius: '50%',
                    }}
                  />
                  {/* Right side flame */}
                  <span
                    style={{
                      position: 'absolute',
                      top: '20%',
                      right: '-15px',
                      width: '18px',
                      height: '25px',
                      background: 'linear-gradient(270deg, rgba(139, 0, 0, 0.8) 0%, transparent 100%)',
                      filter: 'blur(5px) drop-shadow(0 0 8px rgba(0, 0, 0, 0.9))',
                      animation: 'flameRight 1.8s ease-in-out infinite 0.5s',
                      zIndex: 1,
                      pointerEvents: 'none',
                      borderRadius: '50%',
                    }}
                  />
                  {/* Bottom glow with dark base */}
                  <span
                    style={{
                      position: 'absolute',
                      bottom: '-10px',
                      left: '0',
                      width: '100%',
                      height: '20px',
                      background: 'radial-gradient(ellipse at center, rgba(139, 0, 0, 0.5) 0%, rgba(0, 0, 0, 0.4) 40%, transparent 70%)',
                      filter: 'blur(8px)',
                      animation: 'pulse 2s ease-in-out infinite',
                      zIndex: 1,
                      pointerEvents: 'none',
                    }}
                  />
                </span>{' '}
                <span style={{ color: '#8B0000', fontWeight: '800' }}>App</span>
              </h1>

              {/* Subheading */}
              <p
                style={{
                  fontFamily: 'var(--font-inter)',
                  fontWeight: '400',
                  fontSize: '1.125rem',
                  color: '#B0B0B0',
                  lineHeight: '1.5',
                  maxWidth: '600px',
                  marginBottom: '40px',
                  textAlign: 'center',
                  marginLeft: 'auto',
                  marginRight: 'auto',
                }}
              >
                A simple, powerful, and beautiful way to manage your tasks.
              </p>

              {/* CTA Buttons */}
              <div className="flex flex-col sm:flex-row items-center justify-center gap-3 mb-5">
                <Link
                  href="/auth/signup"
                  className="transition-all duration-200"
                  style={{
                    fontFamily: 'var(--font-inter)',
                    fontWeight: '600',
                    fontSize: '1rem',
                    background: '#8B0000',
                    color: '#FFFFFF',
                    padding: '14px 32px',
                    borderRadius: '8px',
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
                  Get Started Free
                </Link>

                <Link
                  href="/auth/signin"
                  className="transition-all duration-200"
                  style={{
                    fontFamily: 'var(--font-inter)',
                    fontWeight: '500',
                    fontSize: '1rem',
                    background: '#242424',
                    color: '#FFFFFF',
                    padding: '14px 32px',
                    borderRadius: '8px',
                    textDecoration: 'none',
                    display: 'inline-block',
                  }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.background = '#2a2a2a';
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.background = '#242424';
                  }}
                >
                  Sign In
                </Link>
              </div>

              {/* Trust Badge */}
              <p
                style={{
                  fontFamily: 'var(--font-inter)',
                  fontWeight: '400',
                  fontSize: '0.8125rem',
                  color: '#808080',
                  marginTop: '20px',
                }}
              >
                No credit card required
              </p>
            </div>
          </div>
        </section>

        {/* Features Section - Grid Layout */}
        <section
          className="w-full flex flex-col items-center justify-center"
          style={{
            background: '#0f0f0f',
            padding: '80px 20px',
          }}
        >
          {/* Features Heading */}
          <h2
            style={{
              fontFamily: 'var(--font-inter)',
              fontWeight: '700',
              fontSize: 'clamp(1.75rem, 3vw, 2.5rem)',
              color: '#FFFFFF',
              textAlign: 'center',
              marginBottom: '60px',
            }}
          >
            Features
          </h2>

          <div className="container mx-auto flex justify-center" style={{ maxWidth: '1100px' }}>
            {/* Features Grid with 1px gap effect */}
            <div
              className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3"
              style={{
                gap: '1px',
                background: '#2a2a2a',
                justifyContent: 'center',
                margin: '0 auto',
                width: '100%',
              }}
            >
              {/* Feature 1 */}
              <div
                style={{
                  background: '#1a1a1a',
                  padding: '48px 32px',
                  textAlign: 'center',
                  display: 'flex',
                  flexDirection: 'column',
                  alignItems: 'center',
                  width: '100%',
                  height: '100%',
                }}
              >
                <div style={{ marginBottom: '24px', display: 'flex', justifyContent: 'center' }}>
                  <svg width="32" height="32" viewBox="0 0 24 24" fill="none" style={{ color: '#8B0000' }}>
                    <path d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                  </svg>
                </div>
                <h3
                  style={{
                    fontFamily: 'var(--font-inter)',
                    fontWeight: '600',
                    fontSize: '1.125rem',
                    color: '#FFFFFF',
                    marginBottom: '12px',
                    textAlign: 'center',
                    width: '100%',
                  }}
                >
                  Easy Management
                </h3>
                <p
                  style={{
                    fontFamily: 'var(--font-inter)',
                    fontWeight: '400',
                    fontSize: '0.9375rem',
                    color: '#B0B0B0',
                    lineHeight: '1.6',
                    textAlign: 'center',
                    width: '100%',
                  }}
                >
                  Simple interface
                </p>
              </div>

              {/* Feature 2 */}
              <div
                style={{
                  background: '#1a1a1a',
                  padding: '48px 32px',
                  textAlign: 'center',
                  display: 'flex',
                  flexDirection: 'column',
                  alignItems: 'center',
                  width: '100%',
                  height: '100%',
                }}
              >
                <div style={{ marginBottom: '24px', display: 'flex', justifyContent: 'center' }}>
                  <svg width="32" height="32" viewBox="0 0 24 24" fill="none" style={{ color: '#8B0000' }}>
                    <path d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                  </svg>
                </div>
                <h3
                  style={{
                    fontFamily: 'var(--font-inter)',
                    fontWeight: '600',
                    fontSize: '1.125rem',
                    color: '#FFFFFF',
                    marginBottom: '12px',
                    textAlign: 'center',
                    width: '100%',
                  }}
                >
                  Secure
                </h3>
                <p
                  style={{
                    fontFamily: 'var(--font-inter)',
                    fontWeight: '400',
                    fontSize: '0.9375rem',
                    color: '#B0B0B0',
                    lineHeight: '1.6',
                    textAlign: 'center',
                    width: '100%',
                  }}
                >
                  Protected data
                </p>
              </div>

              {/* Feature 3 */}
              <div
                style={{
                  background: '#1a1a1a',
                  padding: '48px 32px',
                  textAlign: 'center',
                  display: 'flex',
                  flexDirection: 'column',
                  alignItems: 'center',
                  width: '100%',
                  height: '100%',
                }}
              >
                <div style={{ marginBottom: '24px', display: 'flex', justifyContent: 'center' }}>
                  <svg width="32" height="32" viewBox="0 0 24 24" fill="none" style={{ color: '#8B0000' }}>
                    <path d="M12 18h.01M8 21h8a2 2 0 002-2V5a2 2 0 00-2-2H8a2 2 0 00-2 2v14a2 2 0 002 2z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                  </svg>
                </div>
                <h3
                  style={{
                    fontFamily: 'var(--font-inter)',
                    fontWeight: '600',
                    fontSize: '1.125rem',
                    color: '#FFFFFF',
                    marginBottom: '12px',
                    textAlign: 'center',
                    width: '100%',
                  }}
                >
                  Multi-device
                </h3>
                <p
                  style={{
                    fontFamily: 'var(--font-inter)',
                    fontWeight: '400',
                    fontSize: '0.9375rem',
                    color: '#B0B0B0',
                    lineHeight: '1.6',
                    textAlign: 'center',
                    width: '100%',
                  }}
                >
                  Works everywhere
                </p>
              </div>

              {/* Feature 4 */}
              <div
                style={{
                  background: '#1a1a1a',
                  padding: '48px 32px',
                  textAlign: 'center',
                  display: 'flex',
                  flexDirection: 'column',
                  alignItems: 'center',
                  width: '100%',
                  height: '100%',
                }}
              >
                <div style={{ marginBottom: '24px', display: 'flex', justifyContent: 'center' }}>
                  <svg width="32" height="32" viewBox="0 0 24 24" fill="none" style={{ color: '#8B0000' }}>
                    <path d="M13 10V3L4 14h7v7l9-11h-7z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                  </svg>
                </div>
                <h3
                  style={{
                    fontFamily: 'var(--font-inter)',
                    fontWeight: '600',
                    fontSize: '1.125rem',
                    color: '#FFFFFF',
                    marginBottom: '12px',
                    textAlign: 'center',
                    width: '100%',
                  }}
                >
                  Fast & Efficient
                </h3>
                <p
                  style={{
                    fontFamily: 'var(--font-inter)',
                    fontWeight: '400',
                    fontSize: '0.9375rem',
                    color: '#B0B0B0',
                    lineHeight: '1.6',
                    textAlign: 'center',
                    width: '100%',
                  }}
                >
                  Lightning speed
                </p>
              </div>

              {/* Feature 5 */}
              <div
                style={{
                  background: '#1a1a1a',
                  padding: '48px 32px',
                  textAlign: 'center',
                  display: 'flex',
                  flexDirection: 'column',
                  alignItems: 'center',
                  width: '100%',
                  height: '100%',
                }}
              >
                <div style={{ marginBottom: '24px', display: 'flex', justifyContent: 'center' }}>
                  <svg width="32" height="32" viewBox="0 0 24 24" fill="none" style={{ color: '#8B0000' }}>
                    <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                  </svg>
                </div>
                <h3
                  style={{
                    fontFamily: 'var(--font-inter)',
                    fontWeight: '600',
                    fontSize: '1.125rem',
                    color: '#FFFFFF',
                    marginBottom: '12px',
                    textAlign: 'center',
                    width: '100%',
                  }}
                >
                  Task Tracking
                </h3>
                <p
                  style={{
                    fontFamily: 'var(--font-inter)',
                    fontWeight: '400',
                    fontSize: '0.9375rem',
                    color: '#B0B0B0',
                    lineHeight: '1.6',
                    textAlign: 'center',
                    width: '100%',
                  }}
                >
                  Never miss a beat
                </p>
              </div>

              {/* Feature 6 */}
              <div
                style={{
                  background: '#1a1a1a',
                  padding: '48px 32px',
                  textAlign: 'center',
                  display: 'flex',
                  flexDirection: 'column',
                  alignItems: 'center',
                  width: '100%',
                  height: '100%',
                }}
              >
                <div style={{ marginBottom: '24px', display: 'flex', justifyContent: 'center' }}>
                  <svg width="32" height="32" viewBox="0 0 24 24" fill="none" style={{ color: '#8B0000' }}>
                    <path d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                  </svg>
                </div>
                <h3
                  style={{
                    fontFamily: 'var(--font-inter)',
                    fontWeight: '600',
                    fontSize: '1.125rem',
                    color: '#FFFFFF',
                    marginBottom: '12px',
                    textAlign: 'center',
                    width: '100%',
                  }}
                >
                  Always Available
                </h3>
                <p
                  style={{
                    fontFamily: 'var(--font-inter)',
                    fontWeight: '400',
                    fontSize: '0.9375rem',
                    color: '#B0B0B0',
                    lineHeight: '1.6',
                    textAlign: 'center',
                    width: '100%',
                  }}
                >
                  24/7 access
                </p>
              </div>
            </div>
          </div>
        </section>

        {/* Footer - Ultra Minimal */}
        <footer
          className="w-full flex items-center justify-center"
          style={{
            background: '#0f0f0f',
            borderTop: '1px solid #2a2a2a',
            padding: '40px 20px',
          }}
        >
          <div
            style={{
              fontFamily: 'var(--font-inter)',
              fontWeight: '400',
              fontSize: '0.875rem',
              color: '#808080',
              textAlign: 'center',
            }}
          >
            © 2025 Todo App
          </div>
        </footer>
      </main>
    </>
  );
}
