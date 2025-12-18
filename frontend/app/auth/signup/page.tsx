// T031: Create signup page UI with form validation
// T034: Implement signup form submission with API integration
// T053: Add client-side validation

"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { apiClient } from "@/lib/api";
import { AuthService } from "@/lib/auth";
import Spinner from "@/components/ui/Spinner";
import Header from "@/components/Header";

export default function SignupPage() {
  const router = useRouter();
  const [formData, setFormData] = useState({
    email: "",
    password: "",
    confirmPassword: "",
    display_name: "",
  });
  const [errors, setErrors] = useState<{ [key: string]: string }>({});
  const [isLoading, setIsLoading] = useState(false);
  const [serverError, setServerError] = useState("");
  const [success, setSuccess] = useState(false);

  // Redirect if already authenticated
  useEffect(() => {
    if (AuthService.isAuthenticated()) {
      router.push("/tasks");
    }
  }, [router]);

  const validateForm = (): boolean => {
    const newErrors: { [key: string]: string } = {};

    // Email validation
    if (!formData.email) {
      newErrors.email = "Email is required";
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      newErrors.email = "Please enter a valid email address";
    }

    // Password validation - Strong password requirements
    if (!formData.password) {
      newErrors.password = "Password is required";
    } else {
      const hasMinLength = formData.password.length >= 8;
      const hasUppercase = /[A-Z]/.test(formData.password);
      const hasLowercase = /[a-z]/.test(formData.password);
      const hasNumber = /[0-9]/.test(formData.password);
      const hasSpecialChar = /[!@#$%^&*(),.?":{}|<>]/.test(formData.password);

      if (!hasMinLength || !hasUppercase || !hasLowercase || !hasNumber) {
        newErrors.password = "Password too weak. Must have 8+ characters, uppercase, lowercase, and number";
      }
      // Note: Special character is optional as per requirements
    }

    // Confirm password validation
    if (!formData.confirmPassword) {
      newErrors.confirmPassword = "Please confirm your password";
    } else if (formData.password !== formData.confirmPassword) {
      newErrors.confirmPassword = "Passwords do not match";
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setServerError("");

    if (!validateForm()) {
      return;
    }

    setIsLoading(true);

    try {
      await apiClient.signup({
        email: formData.email,
        password: formData.password,
        display_name: formData.display_name || undefined,
      });

      // Show success message
      setSuccess(true);
      setIsLoading(false);

      // Wait 2 seconds before redirecting (as per documentation)
      setTimeout(() => {
        // Use window.location.href for full page reload to ensure localStorage is committed
        window.location.href = "/tasks";
      }, 2000);
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : "Signup failed. Please try again.";

      // Customize error messages based on backend response
      if (errorMsg.includes("already exists") || errorMsg.includes("409")) {
        setServerError("Account already exists. Try logging in instead.");
      } else if (errorMsg.includes("password") || errorMsg.includes("weak")) {
        setServerError("Password too weak. Must have 8+ characters, uppercase, lowercase, and number.");
      } else {
        setServerError(errorMsg);
      }
      setIsLoading(false);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
    // Clear error for this field when user starts typing
    if (errors[name]) {
      setErrors((prev) => ({ ...prev, [name]: "" }));
    }
    setServerError("");
  };

  return (
    <>
      <Header />
      <div className="min-h-[calc(100vh-4rem)] flex items-center justify-center px-4 py-16 sm:px-6 lg:px-8">
        <div className="w-full max-w-lg space-y-10">
          <div className="text-center">
            <h2 className="text-3xl font-bold tracking-tight">Create your account</h2>
            <p className="mt-6 text-sm text-[var(--foreground)] opacity-70">
              Start organizing your tasks today
            </p>
          </div>

          <form onSubmit={handleSubmit} className="mt-10 space-y-8">
            {success && (
              <div className="p-3 text-sm rounded-lg bg-green-50 dark:bg-green-900/20 text-green-800 dark:text-green-400 border border-green-200 dark:border-green-800">
                <div className="flex items-center gap-2">
                  <svg className="w-5 h-5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                  </svg>
                  <div>
                    <p className="font-semibold">Account created successfully!</p>
                    <p className="text-xs sm:text-sm mt-1">You are now logged in. Redirecting to your dashboard...</p>
                  </div>
                </div>
              </div>
            )}

            {serverError && !success && (
              <div className="p-3 text-sm rounded-lg bg-red-50 dark:bg-red-900/20 text-red-600 dark:text-red-400 border border-red-200 dark:border-red-800">
                <p className="mb-2">{serverError}</p>
                {serverError.includes("already exists") && (
                  <Link href="/auth/signin" className="text-sm font-medium underline hover:no-underline">
                    Go to login →
                  </Link>
                )}
              </div>
            )}

            <div className="space-y-8">
              <div>
                <label htmlFor="email" className="block text-sm font-medium mb-3">
                  Email address *
                </label>
                <input
                  id="email"
                  name="email"
                  type="email"
                  autoComplete="email"
                  required
                  value={formData.email}
                  onChange={handleChange}
                  className={`w-full px-5 py-4 border rounded-lg focus:outline-none focus:ring-2 focus:ring-[var(--primary)] bg-[var(--background)] ${
                    errors.email ? "border-red-500" : "border-[var(--border)]"
                  }`}
                  placeholder="you@example.com"
                />
                {errors.email && <p className="mt-2 text-sm text-red-600 dark:text-red-400">{errors.email}</p>}
              </div>

              <div>
                <label htmlFor="display_name" className="block text-sm font-medium mb-3">
                  Display name (optional)
                </label>
                <input
                  id="display_name"
                  name="display_name"
                  type="text"
                  autoComplete="name"
                  value={formData.display_name}
                  onChange={handleChange}
                  className="w-full px-5 py-4 border border-[var(--border)] rounded-lg focus:outline-none focus:ring-2 focus:ring-[var(--primary)] bg-[var(--background)]"
                  placeholder="John Doe"
                />
              </div>

              <div>
                <label htmlFor="password" className="block text-sm font-medium mb-3">
                  Password *
                </label>
                <input
                  id="password"
                  name="password"
                  type="password"
                  autoComplete="new-password"
                  required
                  value={formData.password}
                  onChange={handleChange}
                  className={`w-full px-5 py-4 border rounded-lg focus:outline-none focus:ring-2 focus:ring-[var(--primary)] bg-[var(--background)] ${
                    errors.password ? "border-red-500" : "border-[var(--border)]"
                  }`}
                  placeholder="8+ chars, uppercase, lowercase, number"
                />
                {errors.password && <p className="mt-2 text-sm text-red-600 dark:text-red-400">{errors.password}</p>}
              </div>

              <div>
                <label htmlFor="confirmPassword" className="block text-sm font-medium mb-3">
                  Confirm password *
                </label>
                <input
                  id="confirmPassword"
                  name="confirmPassword"
                  type="password"
                  autoComplete="new-password"
                  required
                  value={formData.confirmPassword}
                  onChange={handleChange}
                  className={`w-full px-5 py-4 border rounded-lg focus:outline-none focus:ring-2 focus:ring-[var(--primary)] bg-[var(--background)] ${
                    errors.confirmPassword ? "border-red-500" : "border-[var(--border)]"
                  }`}
                  placeholder="Re-enter your password"
                />
                {errors.confirmPassword && (
                  <p className="mt-2 text-sm text-red-600 dark:text-red-400">{errors.confirmPassword}</p>
                )}
              </div>
            </div>

            <button
              type="submit"
              disabled={isLoading || success}
              className="w-full flex justify-center items-center py-4 px-6 border border-transparent rounded-lg shadow-sm text-base font-medium text-white bg-[var(--primary)] hover:bg-[var(--primary-hover)] focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-[var(--primary)] disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {success ? (
                <>
                  <Spinner size="sm" className="mr-2" />
                  Success! Redirecting...
                </>
              ) : isLoading ? (
                <>
                  <Spinner size="sm" className="mr-2" />
                  Creating account...
                </>
              ) : (
                "Create account"
              )}
            </button>

            <div className="text-center text-sm">
              <span className="text-[var(--foreground)] opacity-70">Already have an account? </span>
              <Link href="/auth/signin" className="font-medium text-[var(--primary)] hover:underline">
                Sign in
              </Link>
            </div>
          </form>
        </div>
      </div>
    </>
  );
}
