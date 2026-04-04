import { create } from 'zustand';
import { Task } from '@/types';
import * as taskApi from '@/api/tasks';

interface TaskState {
  tasks: Task[];
  currentTask: Task | null;
  isLoading: boolean;
  fetchTasks: () => Promise<void>;
  fetchTaskById: (id: string) => Promise<void>;
  createTask: (data: any) => Promise<Task>;
  cancelTask: (id: string) => Promise<void>;
}

export const useTaskStore = create<TaskState>((set) => ({
  tasks: [],
  currentTask: null,
  isLoading: false,

  fetchTasks: async () => {
    set({ isLoading: true });
    try {
      const { tasks } = await taskApi.getTasks();
      set({ tasks, isLoading: false });
    } catch (error) {
      set({ isLoading: false });
      throw error;
    }
  },

  fetchTaskById: async (id: string) => {
    set({ isLoading: true });
    try {
      const task = await taskApi.getTaskById(id);
      set({ currentTask: task, isLoading: false });
    } catch (error) {
      set({ isLoading: false });
      throw error;
    }
  },

  createTask: async (data: any) => {
    set({ isLoading: true });
    try {
      const task = await taskApi.createNovelTask(data);
      set((state) => ({
        tasks: [task, ...state.tasks],
        isLoading: false
      }));
      return task;
    } catch (error) {
      set({ isLoading: false });
      throw error;
    }
  },

  cancelTask: async (id: string) => {
    try {
      await taskApi.cancelTask(id);
      set((state) => ({
        tasks: state.tasks.map((task) =>
          task.id === id ? { ...task, status: 'cancelled' as const } : task
        ),
      }));
    } catch (error) {
      throw error;
    }
  },
}));
