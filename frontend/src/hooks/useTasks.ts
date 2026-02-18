'use client';

import { useState, useEffect } from 'react';
import apiClient from '../lib/api';
import { Task, TaskCreate, TaskUpdate } from '../lib/types';

export function useTasks() {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchTasks = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await apiClient.get('/tasks');
      setTasks(response.data.tasks);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to fetch tasks');
    } finally {
      setLoading(false);
    }
  };

  const createTask = async (taskData: TaskCreate) => {
    setError(null);
    try {
      const response = await apiClient.post('/tasks', taskData);
      setTasks([response.data, ...tasks]);
      return response.data;
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to create task');
      throw err;
    }
  };

  const updateTask = async (taskId: number, taskData: TaskUpdate) => {
    setError(null);
    try {
      const response = await apiClient.put(`/tasks/${taskId}`, taskData);
      setTasks(tasks.map(task => task.id === taskId ? response.data : task));
      return response.data;
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to update task');
      throw err;
    }
  };

  const deleteTask = async (taskId: number) => {
    setError(null);
    try {
      await apiClient.delete(`/tasks/${taskId}`);
      setTasks(tasks.filter(task => task.id !== taskId));
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to delete task');
      throw err;
    }
  };

  useEffect(() => {
    fetchTasks();
  }, []);

  return {
    tasks,
    loading,
    error,
    fetchTasks,
    createTask,
    updateTask,
    deleteTask
  };
}
