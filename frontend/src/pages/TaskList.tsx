import { useEffect, useState } from 'react'

export default function TaskList() {
  const [tasks, setTasks] = useState<any[]>([])

  useEffect(() => {
    fetch('/api/tasks', {
      headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
    })
      .then(res => res.json())
      .then(data => setTasks(data))
      .catch(err => console.error(err))
  }, [])

  return (
    <div>
      <div className="topbar">
        <h1>我的任务</h1>
      </div>
      <div className="card">
        {tasks.map(task => (
          <div key={task.id} className="task-item">
            <h3>{task.title}</h3>
            <p>状态: <span className={`badge badge-${task.status === 'running' ? 'green' : task.status === 'queued' ? 'yellow' : 'blue'}`}>{task.status}</span></p>
            <p>进度: {task.progress}%</p>
          </div>
        ))}
      </div>
    </div>
  )
}
