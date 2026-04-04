import { useEffect, useState } from 'react'

export default function NovelList() {
  const [novels, setNovels] = useState<any[]>([])

  useEffect(() => {
    fetch('/api/novels', {
      headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
    })
      .then(res => res.json())
      .then(data => setNovels(data))
      .catch(err => console.error(err))
  }, [])

  return (
    <div>
      <div className="topbar">
        <h1>小说作品</h1>
      </div>
      <div className="card">
        {novels.map(novel => (
          <div key={novel.id} className="task-item">
            <h3>{novel.title}</h3>
            <p>{novel.genre} · {novel.word_count} 字</p>
            <button className="btn btn-primary">下载</button>
          </div>
        ))}
      </div>
    </div>
  )
}
