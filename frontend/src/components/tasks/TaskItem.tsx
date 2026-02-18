'use client';

import { useState } from 'react';
import { Task, TaskUpdate } from '../../lib/types';

interface TaskItemProps {
  task: Task;
  onUpdate: (taskId: number, data: TaskUpdate) => Promise<void>;
  onDelete: (taskId: number) => Promise<void>;
}

export default function TaskItem({ task, onUpdate, onDelete }: TaskItemProps) {
  const [isEditing, setIsEditing] = useState(false);
  const [editTitle, setEditTitle] = useState(task.title);
  const [editDescription, setEditDescription] = useState(task.description || '');
  const [loading, setLoading] = useState(false);

  const handleToggleComplete = async () => {
    setLoading(true);
    try {
      await onUpdate(task.id, { is_completed: !task.is_completed });
    } finally {
      setLoading(false);
    }
  };

  const handleSaveEdit = async () => {
    setLoading(true);
    try {
      await onUpdate(task.id, {
        title: editTitle,
        description: editDescription || null
      });
      setIsEditing(false);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async () => {
    if (confirm('Are you sure you want to delete this task?')) {
      setLoading(true);
      try {
        await onDelete(task.id);
      } finally {
        setLoading(false);
      }
    }
  };

  if (isEditing) {
    return (
      <div style={{
        padding: '1rem',
        border: '1px solid #ddd',
        borderRadius: '8px',
        marginBottom: '1rem',
        backgroundColor: '#fff'
      }}>
        <input
          type="text"
          value={editTitle}
          onChange={(e) => setEditTitle(e.target.value)}
          style={{
            width: '100%',
            padding: '0.5rem',
            marginBottom: '0.5rem',
            border: '1px solid #ccc',
            borderRadius: '4px',
            fontSize: '1rem'
          }}
        />
        <textarea
          value={editDescription}
          onChange={(e) => setEditDescription(e.target.value)}
          rows={3}
          style={{
            width: '100%',
            padding: '0.5rem',
            marginBottom: '0.5rem',
            border: '1px solid #ccc',
            borderRadius: '4px',
            fontSize: '1rem',
            fontFamily: 'inherit'
          }}
        />
        <div style={{ display: 'flex', gap: '0.5rem' }}>
          <button
            onClick={handleSaveEdit}
            disabled={loading}
            style={{
              padding: '0.5rem 1rem',
              backgroundColor: '#28a745',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: loading ? 'not-allowed' : 'pointer'
            }}
          >
            Save
          </button>
          <button
            onClick={() => setIsEditing(false)}
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
            Cancel
          </button>
        </div>
      </div>
    );
  }

  return (
    <div style={{
      padding: '1rem',
      border: '1px solid #ddd',
      borderRadius: '8px',
      marginBottom: '1rem',
      backgroundColor: task.is_completed ? '#f0f8f0' : '#fff'
    }}>
      <div style={{ display: 'flex', alignItems: 'flex-start', gap: '1rem' }}>
        <input
          type="checkbox"
          checked={task.is_completed}
          onChange={handleToggleComplete}
          disabled={loading}
          style={{ marginTop: '0.25rem', cursor: 'pointer' }}
        />
        <div style={{ flex: 1 }}>
          <h3 style={{
            margin: '0 0 0.5rem 0',
            textDecoration: task.is_completed ? 'line-through' : 'none',
            color: task.is_completed ? '#666' : '#000'
          }}>
            {task.title}
          </h3>
          {task.description && (
            <p style={{
              margin: '0 0 0.5rem 0',
              color: '#666',
              whiteSpace: 'pre-wrap'
            }}>
              {task.description}
            </p>
          )}
          <div style={{ fontSize: '0.85rem', color: '#999' }}>
            Created: {new Date(task.created_at).toLocaleString()}
          </div>
        </div>
        <div style={{ display: 'flex', gap: '0.5rem' }}>
          <button
            onClick={() => setIsEditing(true)}
            disabled={loading}
            style={{
              padding: '0.5rem 1rem',
              backgroundColor: '#0070f3',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: loading ? 'not-allowed' : 'pointer'
            }}
          >
            Edit
          </button>
          <button
            onClick={handleDelete}
            disabled={loading}
            style={{
              padding: '0.5rem 1rem',
              backgroundColor: '#dc3545',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: loading ? 'not-allowed' : 'pointer'
            }}
          >
            Delete
          </button>
        </div>
      </div>
    </div>
  );
}
