import { useParams } from 'react-router-dom'

const NovelDetail = () => {
  const { id } = useParams()

  return (
    <div>
      <div className="topbar">
        <h1>小说详情</h1>
      </div>
      <div className="card">
        <p>小说 ID: {id}</p>
        <p>详情页面开发中...</p>
      </div>
    </div>
  )
}

export default NovelDetail
