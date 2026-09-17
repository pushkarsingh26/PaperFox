"use client";

import React, { useState } from "react";
import Link from "next/link";
import { useAuth } from "@/context/AuthContext";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { Card } from "@/components/ui/Card";
import { FoxLogo } from "@/components/ui/FoxLogo";
import { AlertCircle, Mail, Lock, Eye, EyeOff, ArrowRight } from "lucide-react";

export default function LoginPage() {
  const { login, loading, error, clearError } = useAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
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
    <div className="min-h-screen bg-[#090d16] flex flex-col items-center justify-center p-4 selection:bg-amber-500/30 selection:text-amber-200 relative overflow-hidden">
      {/* Ambient background glow */}
      <div className="absolute top-1/4 left-1/2 -translate-x-1/2 w-96 h-96 bg-amber-500/5 rounded-full blur-3xl pointer-events-none" />

      <div className="w-full max-w-md space-y-6 relative z-10">
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
          <h1 className="text-2xl font-bold text-white tracking-tight pt-2">Welcome Back</h1>
          <p className="text-xs text-slate-400">
            Sign in to access your resumes, target jobs, and cold outreach.
          </p>
        </div>

        {/* Login Card */}
        <Card className="p-8 space-y-6 border-slate-800/80 bg-slate-900/70 shadow-2xl">
          {(error || validationError) && (
            <div className="p-3.5 bg-red-500/10 border border-red-500/30 rounded-xl flex items-start space-x-2.5 text-xs text-red-400">
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
              leftIcon={<Mail className="w-4 h-4" />}
              required
            />

            <div className="space-y-1">
              <Input
                label="Password"
                type={showPassword ? "text" : "password"}
                placeholder="••••••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                disabled={loading}
                leftIcon={<Lock className="w-4 h-4" />}
                rightIcon={
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="text-slate-400 hover:text-slate-200 transition-colors"
                    tabIndex={-1}
                  >
                    {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                  </button>
                }
                required
              />
            </div>

            <Button
              type="submit"
              variant="primary"
              size="lg"
              className="w-full text-sm font-semibold mt-2"
              isLoading={loading}
            >
              Sign In to Account
              <ArrowRight className="w-4 h-4 ml-1.5" />
            </Button>
          </form>
        </Card>

        <p className="text-center text-xs text-slate-400">
          Don't have an account yet?{" "}
          <Link
            href="/signup"
            className="text-amber-400 hover:text-amber-300 font-semibold underline underline-offset-4"
          >
            Create free account
          </Link>
        </p>
      </div>
    </div>
  );
}
