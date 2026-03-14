'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '../../hooks/useAuth';
import { useTasks } from '../../hooks/useTasks';
import TaskForm from '../../components/tasks/TaskForm';
import TaskList from '../../components/tasks/TaskList';
import ChatPanel from '../../components/chat/ChatPanel';

export default function DashboardPage() {
  const { user, logout } = useAuth();
  const router = useRouter();
  const { tasks, loading, error, createTask, updateTask, deleteTask, fetchTasks } = useTasks();

  useEffect(() => {
    // Check if user is authenticated
    const token = localStorage.getItem('auth_token');
    if (!token) {
      router.push('/login');
    }
  }, [router]);

  const handleLogout = () => {
    logout();
  };

  return (
    <div style={{ padding: '2rem', maxWidth: '1400px', margin: '0 auto' }}>
      {/* Header */}
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: '2rem',
        paddingBottom: '1rem',
        borderBottom: '2px solid #eee'
      }}>
        <div>
          <h1 style={{ margin: '0 0 0.5rem 0' }}>Task Dashboard</h1>
          {user && <p style={{ margin: 0, color: '#666' }}>Welcome, {user.email}</p>}
        </div>
        <button
          onClick={handleLogout}
          style={{
            padding: '0.75rem 1.5rem',
            backgroundColor: '#dc3545',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer',
            fontSize: '1rem'
          }}
        >
          Logout
        </button>
      </div>

      {/* Two-column layout: Tasks | Chat */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: '1fr 1fr',
        gap: '2rem',
        height: 'calc(100vh - 200px)',
      }}>
        {/* Tasks Section */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem', overflow: 'auto' }}>
          <TaskForm onSubmit={createTask} />
          <TaskList
            tasks={tasks}
            loading={loading}
            error={error}
            onUpdate={updateTask}
            onDelete={deleteTask}
            onRefresh={fetchTasks}
          />
        </div>

        {/* Chat Section */}
        <div>
          <ChatPanel onTaskOperation={fetchTasks} />
        </div>
      </div>

      <style jsx>{`
        @media (max-width: 767px) {
          div[style*="gridTemplateColumns"] {
            grid-template-columns: 1fr !important;
            grid-template-rows: auto 1fr;
            height: auto !important;
          }
        }

        @media (min-width: 768px) and (max-width: 1023px) {
          div[style*="gridTemplateColumns"] {
            grid-template-columns: 2fr 3fr !important;
          }
        }
      `}</style>
    </div>
  );
}
