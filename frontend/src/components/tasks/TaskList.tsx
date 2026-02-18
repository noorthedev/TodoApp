'use client';

import TaskItem from './TaskItem';
import { Task, TaskUpdate } from '../../lib/types';

interface TaskListProps {
  tasks: Task[];
  loading: boolean;
  error: string | null;
  onUpdate: (taskId: number, data: TaskUpdate) => Promise<void>;
  onDelete: (taskId: number) => Promise<void>;
  onRefresh: () => Promise<void>;
}

export default function TaskList({ tasks, loading, error, onUpdate, onDelete, onRefresh }: TaskListProps) {
  if (loading && tasks.length === 0) {
    return <div style={{ textAlign: 'center', padding: '2rem', color: '#666' }}>Loading tasks...</div>;
  }

  if (error) {
    return (
      <div style={{
        padding: '1rem',
        backgroundColor: '#fee',
        color: 'red',
        borderRadius: '4px',
        marginBottom: '1rem'
      }}>
        {error}
        <button
          onClick={onRefresh}
          style={{
            marginLeft: '1rem',
            padding: '0.5rem 1rem',
            backgroundColor: '#dc3545',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer'
          }}
        >
          Retry
        </button>
      </div>
    );
  }

  if (tasks.length === 0) {
    return (
      <div style={{
        textAlign: 'center',
        padding: '3rem',
        backgroundColor: '#f9f9f9',
        borderRadius: '8px',
        color: '#666'
      }}>
        <p style={{ fontSize: '1.2rem', marginBottom: '0.5rem' }}>No tasks yet</p>
        <p>Create your first task above to get started!</p>
      </div>
    );
  }

  return (
    <div>
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: '1rem'
      }}>
        <h2 style={{ margin: 0 }}>Your Tasks ({tasks.length})</h2>
        <button
          onClick={onRefresh}
          disabled={loading}
          style={{
            padding: '0.5rem 1rem',
            backgroundColor: '#6c757d',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: loading ? 'not-allowed' : 'pointer'
          }}
        >
          {loading ? 'Refreshing...' : 'Refresh'}
        </button>
      </div>

      {tasks.map(task => (
        <TaskItem
          key={task.id}
          task={task}
          onUpdate={onUpdate}
          onDelete={onDelete}
        />
      ))}
    </div>
  );
}
