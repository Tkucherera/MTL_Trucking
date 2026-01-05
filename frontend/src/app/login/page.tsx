'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useForm } from 'react-hook-form';
import { Lock, Mail, Smartphone, LogIn } from 'lucide-react';
import { authApi, driverApi } from '@/lib/api';
import { useAuthStore } from '@/lib/store';

type AuthMethod = 'password' | 'email-otp';

export default function LoginPage() {
  const router = useRouter();
  const setAuth = useAuthStore((state) => state.setAuth);
  const [authMethod, setAuthMethod] = useState<AuthMethod>('password');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [otpStep, setOtpStep] = useState<'initial' | 'verify' | 'email-sent'>('initial');
  const [tempToken, setTempToken] = useState('');
  const [emailForOTP, setEmailForOTP] = useState('');

  const { register, handleSubmit, formState: { errors } } = useForm();

  const onPasswordLogin = async (data: any) => {
    setLoading(true);
    setError('');

    try {
      const response = await authApi.login(data.username, data.password);

      if (response.data.requires_otp) {
        setTempToken(response.data.temp_token);
        setOtpStep('verify');
      } else {
        const { tokens, user } = response.data;
        localStorage.setItem('access_token', tokens.access);
        localStorage.setItem('refresh_token', tokens.refresh);

        // Fetch driver profile if role is DRIVER
        if (user.role === 'DRIVER') {
          const driverResponse = await driverApi.getProfile();
          setAuth(user, driverResponse.data);
        } else {
          setAuth(user);
        }

        router.push('/dashboard');
      }
    } catch (err: any) {
      setError(err.response?.data?.error || 'Login failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const onVerifyOTP = async (data: any) => {
    setLoading(true);
    setError('');

    try {
      const response = await authApi.verifyOTP(tempToken, data.otp_code);
      const { tokens, user } = response.data;

      localStorage.setItem('access_token', tokens.access);
      localStorage.setItem('refresh_token', tokens.refresh);

      if (user.role === 'DRIVER') {
        const driverResponse = await driverApi.getProfile();
        setAuth(user, driverResponse.data);
      } else {
        setAuth(user);
      }

      router.push('/dashboard');
    } catch (err: any) {
      setError(err.response?.data?.error || 'Invalid OTP code');
    } finally {
      setLoading(false);
    }
  };

  const onRequestEmailOTP = async (data: any) => {
    setLoading(true);
    setError('');

    try {
      await authApi.requestEmailOTP(data.email);
      setEmailForOTP(data.email);
      setOtpStep('email-sent');
    } catch (err: any) {
      setError(err.response?.data?.error || 'Failed to send OTP');
    } finally {
      setLoading(false);
    }
  };

  const onVerifyEmailOTP = async (data: any) => {
    setLoading(true);
    setError('');

    try {
      const response = await authApi.verifyEmailOTP(emailForOTP, data.email_otp_code);
      const { tokens, user } = response.data;

      localStorage.setItem('access_token', tokens.access);
      localStorage.setItem('refresh_token', tokens.refresh);

      if (user.role === 'DRIVER') {
        const driverResponse = await driverApi.getProfile();
        setAuth(user, driverResponse.data);
      } else {
        setAuth(user);
      }

      router.push('/dashboard');
    } catch (err: any) {
      setError(err.response?.data?.error || 'Invalid OTP code');
    } finally {
      setLoading(false);
    }
  };

  const renderPasswordLogin = () => (
    <form onSubmit={handleSubmit(onPasswordLogin)} className="space-y-4">
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Username
        </label>
        <input
          type="text"
          {...register('username', { required: 'Username is required' })}
          className="input"
          placeholder="Enter your username"
        />
        {errors.username && (
          <p className="text-red-500 text-sm mt-1">{errors.username.message as string}</p>
        )}
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Password
        </label>
        <input
          type="password"
          {...register('password', { required: 'Password is required' })}
          className="input"
          placeholder="Enter your password"
        />
        {errors.password && (
          <p className="text-red-500 text-sm mt-1">{errors.password.message as string}</p>
        )}
      </div>

      <button type="submit" disabled={loading} className="btn-primary w-full">
        {loading ? 'Logging in...' : 'Login'}
      </button>
    </form>
  );

  const renderOTPVerification = () => (
    <form onSubmit={handleSubmit(onVerifyOTP)} className="space-y-4">
      <div className="text-center mb-6">
        <Smartphone className="w-12 h-12 text-primary-600 mx-auto mb-3" />
        <h3 className="text-lg font-semibold">Enter OTP Code</h3>
        <p className="text-sm text-gray-600">
          Enter the 6-digit code from your authenticator app
        </p>
      </div>

      <div>
        <input
          type="text"
          {...register('otp_code', {
            required: 'OTP code is required',
            pattern: {
              value: /^\d{6}$/,
              message: 'OTP must be 6 digits',
            },
          })}
          className="input text-center text-2xl tracking-widest"
          placeholder="000000"
          maxLength={6}
        />
        {errors.otp_code && (
          <p className="text-red-500 text-sm mt-1">{errors.otp_code.message as string}</p>
        )}
      </div>

      <button type="submit" disabled={loading} className="btn-primary w-full">
        {loading ? 'Verifying...' : 'Verify OTP'}
      </button>

      <button
        type="button"
        onClick={() => {
          setOtpStep('initial');
          setError('');
        }}
        className="btn-secondary w-full"
      >
        Back to Login
      </button>
    </form>
  );

  const renderEmailOTPRequest = () => (
    <form onSubmit={handleSubmit(onRequestEmailOTP)} className="space-y-4">
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Email Address
        </label>
        <input
          type="email"
          {...register('email', {
            required: 'Email is required',
            pattern: {
              value: /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i,
              message: 'Invalid email address',
            },
          })}
          className="input"
          placeholder="Enter your email"
        />
        {errors.email && (
          <p className="text-red-500 text-sm mt-1">{errors.email.message as string}</p>
        )}
      </div>

      <button type="submit" disabled={loading} className="btn-primary w-full">
        {loading ? 'Sending...' : 'Send OTP to Email'}
      </button>
    </form>
  );

  const renderEmailOTPVerification = () => (
    <form onSubmit={handleSubmit(onVerifyEmailOTP)} className="space-y-4">
      <div className="text-center mb-6">
        <Mail className="w-12 h-12 text-primary-600 mx-auto mb-3" />
        <h3 className="text-lg font-semibold">Check Your Email</h3>
        <p className="text-sm text-gray-600">
          We sent a 6-digit code to {emailForOTP}
        </p>
      </div>

      <div>
        <input
          type="text"
          {...register('email_otp_code', {
            required: 'OTP code is required',
            pattern: {
              value: /^\d{6}$/,
              message: 'OTP must be 6 digits',
            },
          })}
          className="input text-center text-2xl tracking-widest"
          placeholder="000000"
          maxLength={6}
        />
        {errors.email_otp_code && (
          <p className="text-red-500 text-sm mt-1">
            {errors.email_otp_code.message as string}
          </p>
        )}
      </div>

      <button type="submit" disabled={loading} className="btn-primary w-full">
        {loading ? 'Verifying...' : 'Verify OTP'}
      </button>

      <button
        type="button"
        onClick={() => {
          setOtpStep('initial');
          setEmailForOTP('');
          setError('');
        }}
        className="btn-secondary w-full"
      >
        Back
      </button>
    </form>
  );

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 via-blue-50 to-indigo-50 flex items-center justify-center p-4">
      <div className="max-w-md w-full">
        {/* Logo and Title */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-primary-600 rounded-2xl mb-4">
            <svg
              className="w-10 h-10 text-white"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
              />
            </svg>
          </div>
          <h1 className="text-3xl font-bold text-gray-900">Driver Portal</h1>
          <p className="text-gray-600 mt-2">Sign in to access your dashboard</p>
        </div>

        {/* Login Card */}
        <div className="card">
          {/* Authentication Method Selector */}
          {otpStep === 'initial' && (
            <div className="mb-6">
              <div className="grid grid-cols-2 gap-3">
                <button
                  type="button"
                  onClick={() => setAuthMethod('password')}
                  className={`p-4 rounded-lg border-2 transition-all ${
                    authMethod === 'password'
                      ? 'border-primary-600 bg-primary-50'
                      : 'border-gray-200 hover:border-gray-300'
                  }`}
                >
                  <Lock className="w-6 h-6 mx-auto mb-2 text-primary-600" />
                  <p className="text-sm font-medium">Password</p>
                </button>

                <button
                  type="button"
                  onClick={() => setAuthMethod('email-otp')}
                  className={`p-4 rounded-lg border-2 transition-all ${
                    authMethod === 'email-otp'
                      ? 'border-primary-600 bg-primary-50'
                      : 'border-gray-200 hover:border-gray-300'
                  }`}
                >
                  <Mail className="w-6 h-6 mx-auto mb-2 text-primary-600" />
                  <p className="text-sm font-medium">Email OTP</p>
                </button>
              </div>
            </div>
          )}

          {/* Error Message */}
          {error && (
            <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg text-red-600 text-sm">
              {error}
            </div>
          )}

          {/* Form Content */}
          {otpStep === 'initial' && authMethod === 'password' && renderPasswordLogin()}
          {otpStep === 'verify' && renderOTPVerification()}
          {otpStep === 'initial' && authMethod === 'email-otp' && renderEmailOTPRequest()}
          {otpStep === 'email-sent' && renderEmailOTPVerification()}
        </div>

        {/* Footer */}
        <div className="text-center mt-6 text-sm text-gray-600">
          <p>Need help? Contact your fleet manager</p>
        </div>
      </div>
    </div>
  );
}