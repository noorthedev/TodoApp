'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '../../hooks/useAuth';
import { useTasks } from '../../hooks/useTasks';
import TaskForm from '../../components/tasks/TaskForm';
import TaskList from '../../components/tasks/TaskList';

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
    <div style={{ padding: '2rem', maxWidth: '900px', margin: '0 auto' }}>
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
  );
}
