import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useTaskStore } from '@/store/taskStore'
import { CreationMode, NovelConfig, VideoConfig } from '@/types'

const CreateTask = () => {
  const navigate = useNavigate()
  const { createTask } = useTaskStore()
  const [mode, setMode] = useState<CreationMode>('novel_only')
  const [novelConfig, setNovelConfig] = useState<NovelConfig>({
    length: 'medium',
    category: 'male',
    subCategories: ['玄幻', '军事'],
    apiPreference: 'auto'
  })
  const [videoConfig, setVideoConfig] = useState<VideoConfig>({
    mode: 'ai_generated',
    enableVoice: true,
    lipSync: false,
    voiceSpeed: 100,
    voiceType: '默认',
    enableSubtitle: true,
    enableMusic: true,
    subtitleFont: '默认',
    subtitleColor: '#FFFFFF',
    subtitlePosition: 'bottom'
  })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      await createTask({
        mode,
        novelConfig,
        videoConfig: mode !== 'novel_only' ? videoConfig : undefined
      })
      navigate('/tasks')
    } catch (err: any) {
      setError(err.response?.data?.message || '创建任务失败')
    } finally {
      setLoading(false)
    }
  }

  const toggleSubCategory = (sub: string) => {
    setNovelConfig(prev => ({
      ...prev,
      subCategories: prev.subCategories.includes(sub)
        ? prev.subCategories.filter(s => s !== sub)
        : [...prev.subCategories, sub]
    }))
  }

  return (
    <div>
      <div className="topbar">
        <h1>创建任务</h1>
      </div>

      {error && (
        <div style={{
          padding: '12px',
          background: '#fee2e2',
          color: '#dc2626',
          borderRadius: '8px',
          marginBottom: '16px'
        }}>
          {error}
        </div>
      )}

      <form onSubmit={handleSubmit}>
        {/* Step 1 - 选择创作方式 */}
        <div className="card">
          <h2>Step 1 — 选择创作方式</h2>
          <div className="mode-grid">
            <div
              className={`mode-card ${mode === 'novel_only' ? 'selected' : ''}`}
              onClick={() => setMode('novel_only')}
            >
              <div className="icon">📖</div>
              <h3>只生成小说</h3>
              <p>微/短/中/长/超长篇</p>
            </div>
            <div
              className={`mode-card ${mode === 'novel_video' ? 'selected' : ''}`}
              onClick={() => setMode('novel_video')}
            >
              <div className="icon">📖🎬</div>
              <h3>小说 + 视频</h3>
              <p>AI 创作并自动制作视频</p>
            </div>
            <div
              className={`mode-card ${mode === 'external_video' ? 'selected' : ''}`}
              onClick={() => setMode('external_video')}
            >
              <div className="icon">📥🎬</div>
              <h3>外部小说 → 视频</h3>
              <p>导入已有小说生成视频</p>
            </div>
            <div
              className={`mode-card ${mode === 'news_video' ? 'selected' : ''}`}
              onClick={() => setMode('news_video')}
            >
              <div className="icon">📰🎬</div>
              <h3>资讯 → 视频</h3>
              <p>新闻资讯智能视频化</p>
            </div>
          </div>
        </div>

        {/* Step 2 - 小说配置 */}
        {mode !== 'news_video' && (
          <div className="card">
            <h2>Step 2 — 小说配置</h2>
            <div className="form-group">
              <label>篇幅选择</label>
              <div className="options">
                {[
                  { value: 'micro', label: '微小说 (1-5千字)' },
                  { value: 'short', label: '短篇 (0.5-3万字)' },
                  { value: 'medium', label: '中篇 (3-10万字)' },
                  { value: 'long', label: '长篇 (10-50万字)' },
                  { value: 'super_long', label: '超长篇 (50万+)' },
                  { value: 'random', label: '🎲 随机' }
                ].map(item => (
                  <div
                    key={item.value}
                    className={`option ${novelConfig.length === item.value ? 'selected' : ''}`}
                    onClick={() => setNovelConfig({ ...novelConfig, length: item.value as any })}
                  >
                    {item.label}
                  </div>
                ))}
              </div>
            </div>

            <div className="form-group">
              <label>题材选择</label>
              <div className="options">
                {[
                  { value: 'children', label: '👶 儿童故事' },
                  { value: 'male', label: '🗡️ 男频' },
                  { value: 'female', label: '💕 女频' },
                  { value: 'random', label: '🎲 随机' }
                ].map(item => (
                  <div
                    key={item.value}
                    className={`option ${novelConfig.category === item.value ? 'selected' : ''}`}
                    onClick={() => setNovelConfig({ ...novelConfig, category: item.value as any, subCategories: [] })}
                  >
                    {item.label}
                  </div>
                ))}
              </div>
            </div>

            {novelConfig.category === 'male' && (
              <div className="form-group">
                <label>男频子分类 (可多选)</label>
                <div className="options">
                  {['玄幻', '仙侠', '军事', '都市', '科幻', '历史', '游戏', '悬疑', '言情', '🎲 随机'].map(sub => (
                    <div
                      key={sub}
                      className={`option ${novelConfig.subCategories.includes(sub) ? 'selected' : ''}`}
                      onClick={() => toggleSubCategory(sub)}
                    >
                      {sub}
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {/* Step 3 - 视频配置 */}
        {mode !== 'novel_only' && (
          <div className="card">
            <h2>Step 3 — 视频配置</h2>
            <div className="form-group">
              <label>画面模式</label>
              <div className="options">
                {[
                  { value: 'ai_generated', label: '🎨 AI 生成画面' },
                  { value: 'image_only', label: '🖼️ 纯图片' },
                  { value: 'imported', label: '📥 导入素材' },
                  { value: 'random', label: '🎲 随机' }
                ].map(item => (
                  <div
                    key={item.value}
                    className={`option ${videoConfig.mode === item.value ? 'selected' : ''}`}
                    onClick={() => setVideoConfig({ ...videoConfig, mode: item.value as any })}
                  >
                    {item.label}
                  </div>
                ))}
              </div>
            </div>

            <div className="form-group">
              <label>语音与字幕</label>
              <div className="options">
                <div
                  className={`option ${videoConfig.enableVoice ? 'selected' : ''}`}
                  onClick={() => setVideoConfig({ ...videoConfig, enableVoice: !videoConfig.enableVoice })}
                >
                  启用语音
                </div>
                <div
                  className={`option ${videoConfig.enableSubtitle ? 'selected' : ''}`}
                  onClick={() => setVideoConfig({ ...videoConfig, enableSubtitle: !videoConfig.enableSubtitle })}
                >
                  启用字幕
                </div>
                <div
                  className={`option ${videoConfig.enableMusic ? 'selected' : ''}`}
                  onClick={() => setVideoConfig({ ...videoConfig, enableMusic: !videoConfig.enableMusic })}
                >
                  背景音乐
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Step 4 - API 偏好与确认 */}
        <div className="card">
          <h2>Step 4 — API 偏好与确认</h2>
          <div className="form-group">
            <label>API 偏好</label>
            <div className="options">
              {[
                { value: 'auto', label: '🤖 全自动' },
                { value: 'deepseek', label: 'DeepSeek' },
                { value: 'gemini', label: 'Gemini' },
                { value: 'openai', label: 'OpenAI' }
              ].map(item => (
                <div
                  key={item.value}
                  className={`option ${novelConfig.apiPreference === item.value ? 'selected' : ''}`}
                  onClick={() => setNovelConfig({ ...novelConfig, apiPreference: item.value as any })}
                >
                  {item.label}
                </div>
              ))}
            </div>
          </div>

          <div style={{ background: '#f8fafc', borderRadius: '8px', padding: '16px', marginBottom: '16px' }}>
            <p style={{ fontSize: '0.9rem', color: '#64748b' }}>
              预估消费：<strong style={{ color: '#1e293b' }}>¥ 8.50 ~ 12.00</strong>
            </p>
          </div>

          <button
            type="submit"
            className="btn btn-primary"
            style={{ width: '100%', padding: '14px', fontSize: '1rem' }}
            disabled={loading}
          >
            {loading ? '创建中...' : '🚀 开始创建'}
          </button>
        </div>
      </form>
    </div>
  )
}

export default CreateTask
