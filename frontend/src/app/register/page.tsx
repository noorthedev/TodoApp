import Link from 'next/link';
import RegisterForm from '../../components/auth/RegisterForm';

export default function RegisterPage() {
  return (
    <div className="auth-container">
      <div className="auth-card">
        {/* Header Section */}
        <div className="auth-header">
          <h1 className="auth-title">Create Account</h1>
          <p className="auth-subtitle">
            Join us to start managing your tasks efficiently
          </p>
        </div>

        {/* The Registration Form */}
        <RegisterForm />

        {/* Footer Links */}
        <div className="auth-footer">
          <p style={{ color: '#64748b', fontSize: '0.9rem', margin: 0 }}>
            Already have an account?{' '}
            <Link href="/login" className="link-text">
              Login here
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