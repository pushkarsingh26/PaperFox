"use client";

import React, { useState } from "react";
import Link from "next/link";
import { useAuth } from "@/context/AuthContext";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { Card } from "@/components/ui/Card";
import { FoxLogo } from "@/components/ui/FoxLogo";
import { AlertCircle } from "lucide-react";

export default function LoginPage() {
  const { login, loading, error, clearError } = useAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [validationError, setValidationError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setValidationError(null);
    clearError();

    if (!email.trim()) {
      setValidationError("Please enter your email address.");
      return;
    }
    if (!password) {
      setValidationError("Please enter your password.");
      return;
    }

    try {
      await login({ email, password });
    } catch (err) {
      // Error handles inside AuthContext state
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 flex flex-col items-center justify-center p-4 selection:bg-amber-500/30 selection:text-amber-200">
      <div className="w-full max-w-md space-y-6">
        {/* Brand Header */}
        <div className="text-center space-y-2">
          <Link href="/" className="inline-flex items-center space-x-2.5 group">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-amber-600/20 to-amber-400/20 border border-amber-500/30 flex items-center justify-center shadow-lg shadow-amber-500/10 group-hover:scale-105 transition-transform duration-200 p-1.5">
              <FoxLogo className="w-7 h-7" size={28} priority />
            </div>
            <span className="font-bold text-2xl text-white tracking-tight">
              Paper<span className="text-amber-500">Fox</span>
            </span>
          </Link>
          <h1 className="text-xl font-bold text-white pt-2">Welcome Back</h1>
          <p className="text-xs text-slate-400">
            Enter your credentials to access your candidate session
          </p>
        </div>

        {/* Login Card */}
        <Card className="p-8 space-y-6">
          {(error || validationError) && (
            <div className="p-3.5 bg-red-500/10 border border-red-500/30 rounded-lg flex items-start space-x-2.5 text-xs text-red-400">
              <AlertCircle className="w-4 h-4 text-red-400 shrink-0 mt-0.5" />
              <span>{validationError || error}</span>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <Input
              label="Email Address"
              type="email"
              placeholder="candidate@example.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              disabled={loading}
              required
            />

            <Input
              label="Password"
              type="password"
              placeholder="••••••••••••"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              disabled={loading}
              required
            />

            <Button
              type="submit"
              variant="primary"
              size="lg"
              className="w-full text-sm font-semibold"
              isLoading={loading}
            >
              Sign In
            </Button>
          </form>
        </Card>

        <p className="text-center text-xs text-slate-400">
          Don't have an account yet?{" "}
          <Link
            href="/signup"
            className="text-amber-400 hover:text-amber-300 font-semibold underline underline-offset-4"
          >
            Sign up now
          </Link>
        </p>
      </div>
    </div>
  );
}
