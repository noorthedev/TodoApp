import Link from 'next/link';
import LoginForm from '../../components/auth/LoginForm';

export default function LoginPage() {
  return (
    <div className="auth-container">
      <div className="auth-card">
        {/* Header */}
        <div className="auth-header">
          <h1 className="auth-title">Welcome Back</h1>
          <p className="auth-subtitle">
            Sign in to access your secure tasks
          </p>
        </div>

        {/* The Form Component */}
        <LoginForm />

        {/* Footer Links */}
        <div className="auth-footer">
          <p style={{ color: '#64748b', fontSize: '0.9rem', margin: 0 }}>
            Don't have an account?{' '}
            <Link href="/register" className="link-text">
              Register here
            </Link>
          </p>
          
          <Link href="/" className="back-link">
            ← Back to home
          </Link>
        </div>
      </div>
    </div>
  );
}