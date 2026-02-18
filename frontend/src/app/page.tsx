import Link from 'next/link';

export default function Home() {
  const features = [
    'Secure Multi-user Authentication',
    'Task Creation & Management',
    'Custom Status Tracking',
    'Private Data Isolation'
  ];

  return (
    <div className="home-container">
      <div className="main-card">
        {/* Header */}
        <header>
          <h1 className="title">
            Todo <span>Application</span>
          </h1>
          <p className="subtitle">
            A streamlined multi-user system to organize your tasks and boost productivity.
          </p>
        </header>

        {/* Buttons */}
        <div className="button-group">
          <Link href="/login" className="btn btn-primary">
            Sign In to Account
          </Link>
          <Link href="/register" className="btn btn-outline">
            Create New Account
          </Link>
        </div>

        {/* Features List */}
        <div className="features-box">
          <ul className="feature-list">
            {features.map((feature, index) => (
              <li key={index} className="feature-item">
                <span className="checkmark">✓</span>
                {feature}
              </li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
}