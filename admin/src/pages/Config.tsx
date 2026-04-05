import { useEffect, useState } from 'react'
import { configApi } from '../api'

export default function Config() {
  const [configs, setConfigs] = useState<any>({})
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)

  // 套餐定价
  const [pricing, setPricing] = useState({
    basic: { novel: 0.05, video: 0 },
    advanced: { novel: 0.08, video: 0.15 },
    professional: { novel: 0.10, video: 0.20 },
    enterprise: { novel: 0, video: 0 },
  })

  // 系统参数
  const [systemParams, setSystemParams] = useState({
    billing_multiplier_min: 1.1,
    billing_multiplier_max: 1.2,
    max_concurrent_tasks: 20,
    publish_mode: 'mock',
  })

  // API密钥配置
  const [apiKeys, setApiKeys] = useState({
    openai_api_key: '',
    openai_base_url: 'https://api.openai.com/v1',
    video_api_key: '',
    video_api_url: '',
    tts_api_key: '',
    tts_api_url: '',
    image_api_key: '',
    image_api_url: '',
  })

  useEffect(() => {
    loadConfigs()
  }, [])

  const loadConfigs = async () => {
    try {
      const data = await configApi.getAll() as any
      setConfigs(data)

      // 解析配置
      if (data.pricing) {
        setPricing(data.pricing.value)
      }
      if (data.system_params) {
        setSystemParams(data.system_params.value)
      }
      if (data.api_keys) {
        setApiKeys(data.api_keys.value)
      }
    } catch (error) {
      console.error('加载配置失败:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleSavePricing = async () => {
    setSaving(true)
    try {
      await configApi.update({
        key: 'pricing',
        value: pricing,
        description: '套餐定价配置',
      })
      alert('套餐定价已保存')
    } catch (error) {
      alert('保存失败')
    } finally {
      setSaving(false)
    }
  }

  const handleSaveSystemParams = async () => {
    setSaving(true)
    try {
      await configApi.update({
        key: 'system_params',
        value: systemParams,
        description: '系统参数配置',
      })
      alert('系统参数已保存')
    } catch (error) {
      alert('保存失败')
    } finally {
      setSaving(false)
    }
  }

  const handleSaveApiKeys = async () => {
    setSaving(true)
    try {
      await configApi.update({
        key: 'api_keys',
        value: apiKeys,
        description: 'API密钥配置',
      })
      alert('API密钥已保存')
    } catch (error) {
      alert('保存失败')
    } finally {
      setSaving(false)
    }
  }

  if (loading) {
    return <div className="text-center py-12">加载中...</div>
  }

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">系统配置</h1>

      {/* 套餐定价 */}
      <div className="bg-white rounded-xl p-6 border border-gray-200 mb-4">
        <h2 className="text-lg font-semibold mb-4">套餐定价</h2>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="bg-gray-50 border-b border-gray-200">
                <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600">套餐</th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600">小说单价(千字)</th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600">视频单价(秒)</th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600">API限额</th>
              </tr>
            </thead>
            <tbody>
              <tr className="border-b border-gray-100">
                <td className="px-4 py-3 font-medium">基础版</td>
                <td className="px-4 py-3">
                  <input
                    type="number"
                    step="0.01"
                    value={pricing.basic.novel}
                    onChange={(e) => setPricing({
                      ...pricing,
                      basic: { ...pricing.basic, novel: parseFloat(e.target.value) }
                    })}
                    className="w-24 px-2 py-1 border border-gray-300 rounded text-sm"
                  />
                </td>
                <td className="px-4 py-3 text-gray-500">-</td>
                <td className="px-4 py-3 text-gray-500">-</td>
              </tr>
              <tr className="border-b border-gray-100">
                <td className="px-4 py-3 font-medium">进阶版</td>
                <td className="px-4 py-3">
                  <input
                    type="number"
                    step="0.01"
                    value={pricing.advanced.novel}
                    onChange={(e) => setPricing({
                      ...pricing,
                      advanced: { ...pricing.advanced, novel: parseFloat(e.target.value) }
                    })}
                    className="w-24 px-2 py-1 border border-gray-300 rounded text-sm"
                  />
                </td>
                <td className="px-4 py-3">
                  <input
                    type="number"
                    step="0.01"
                    value={pricing.advanced.video}
                    onChange={(e) => setPricing({
                      ...pricing,
                      advanced: { ...pricing.advanced, video: parseFloat(e.target.value) }
                    })}
                    className="w-24 px-2 py-1 border border-gray-300 rounded text-sm"
                  />
                </td>
                <td className="px-4 py-3 text-gray-500">-</td>
              </tr>
              <tr className="border-b border-gray-100">
                <td className="px-4 py-3 font-medium">专业版</td>
                <td className="px-4 py-3">
                  <input
                    type="number"
                    step="0.01"
                    value={pricing.professional.novel}
                    onChange={(e) => setPricing({
                      ...pricing,
                      professional: { ...pricing.professional, novel: parseFloat(e.target.value) }
                    })}
                    className="w-24 px-2 py-1 border border-gray-300 rounded text-sm"
                  />
                </td>
                <td className="px-4 py-3">
                  <input
                    type="number"
                    step="0.01"
                    value={pricing.professional.video}
                    onChange={(e) => setPricing({
                      ...pricing,
                      professional: { ...pricing.professional, video: parseFloat(e.target.value) }
                    })}
                    className="w-24 px-2 py-1 border border-gray-300 rounded text-sm"
                  />
                </td>
                <td className="px-4 py-3">1000/天</td>
              </tr>
              <tr>
                <td className="px-4 py-3 font-medium">企业版</td>
                <td className="px-4 py-3 text-gray-500">定制</td>
                <td className="px-4 py-3 text-gray-500">定制</td>
                <td className="px-4 py-3">无限</td>
              </tr>
            </tbody>
          </table>
        </div>
        <button
          onClick={handleSavePricing}
          disabled={saving}
          className="mt-4 px-4 py-2 bg-indigo-600 text-white rounded-lg text-sm font-medium hover:bg-indigo-700 disabled:opacity-50"
        >
          {saving ? '保存中...' : '保存定价'}
        </button>
      </div>

      {/* 系统参数 */}
      <div className="bg-white rounded-xl p-6 border border-gray-200 mb-4">
        <h2 className="text-lg font-semibold mb-4">系统参数</h2>
        <div className="space-y-4 max-w-md">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              计费倍率范围
            </label>
            <div className="flex items-center gap-2">
              <input
                type="number"
                step="0.01"
                value={systemParams.billing_multiplier_min}
                onChange={(e) => setSystemParams({
                  ...systemParams,
                  billing_multiplier_min: parseFloat(e.target.value)
                })}
                className="w-24 px-3 py-2 border border-gray-300 rounded-lg text-sm"
              />
              <span className="text-gray-500">~</span>
              <input
                type="number"
                step="0.01"
                value={systemParams.billing_multiplier_max}
                onChange={(e) => setSystemParams({
                  ...systemParams,
                  billing_multiplier_max: parseFloat(e.target.value)
                })}
                className="w-24 px-3 py-2 border border-gray-300 rounded-lg text-sm"
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              最大并发任务数
            </label>
            <input
              type="number"
              value={systemParams.max_concurrent_tasks}
              onChange={(e) => setSystemParams({
                ...systemParams,
                max_concurrent_tasks: parseInt(e.target.value)
              })}
              className="w-32 px-3 py-2 border border-gray-300 rounded-lg text-sm"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              发布模式
            </label>
            <select
              value={systemParams.publish_mode}
              onChange={(e) => setSystemParams({
                ...systemParams,
                publish_mode: e.target.value
              })}
              className="px-3 py-2 border border-gray-300 rounded-lg text-sm"
            >
              <option value="mock">mock (模拟)</option>
              <option value="production">production (生产)</option>
            </select>
          </div>

          <button
            onClick={handleSaveSystemParams}
            disabled={saving}
            className="px-4 py-2 bg-indigo-600 text-white rounded-lg text-sm font-medium hover:bg-indigo-700 disabled:opacity-50"
          >
            {saving ? '保存中...' : '保存配置'}
          </button>
        </div>
      </div>

      {/* API密钥配置 */}
      <div className="bg-white rounded-xl p-6 border border-gray-200">
        <h2 className="text-lg font-semibold mb-4">API密钥配置</h2>
        <div className="space-y-6 max-w-2xl">
          {/* OpenAI配置 */}
          <div className="border-b border-gray-200 pb-4">
            <h3 className="text-md font-medium text-gray-900 mb-3">OpenAI (小说生成)</h3>
            <div className="space-y-3">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  API Key
                </label>
                <input
                  type="password"
                  value={apiKeys.openai_api_key}
                  onChange={(e) => setApiKeys({
                    ...apiKeys,
                    openai_api_key: e.target.value
                  })}
                  placeholder="sk-..."
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Base URL
                </label>
                <input
                  type="text"
                  value={apiKeys.openai_base_url}
                  onChange={(e) => setApiKeys({
                    ...apiKeys,
                    openai_base_url: e.target.value
                  })}
                  placeholder="https://api.openai.com/v1"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm"
                />
              </div>
            </div>
          </div>

          {/* 视频生成配置 */}
          <div className="border-b border-gray-200 pb-4">
            <h3 className="text-md font-medium text-gray-900 mb-3">视频生成服务</h3>
            <div className="space-y-3">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  API Key
                </label>
                <input
                  type="password"
                  value={apiKeys.video_api_key}
                  onChange={(e) => setApiKeys({
                    ...apiKeys,
                    video_api_key: e.target.value
                  })}
                  placeholder="输入视频生成API密钥"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  API URL
                </label>
                <input
                  type="text"
                  value={apiKeys.video_api_url}
                  onChange={(e) => setApiKeys({
                    ...apiKeys,
                    video_api_url: e.target.value
                  })}
                  placeholder="https://api.example.com/video"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm"
                />
              </div>
            </div>
          </div>

          {/* 语音合成配置 */}
          <div className="border-b border-gray-200 pb-4">
            <h3 className="text-md font-medium text-gray-900 mb-3">语音合成服务 (TTS)</h3>
            <div className="space-y-3">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  API Key
                </label>
                <input
                  type="password"
                  value={apiKeys.tts_api_key}
                  onChange={(e) => setApiKeys({
                    ...apiKeys,
                    tts_api_key: e.target.value
                  })}
                  placeholder="输入语音合成API密钥"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  API URL
                </label>
                <input
                  type="text"
                  value={apiKeys.tts_api_url}
                  onChange={(e) => setApiKeys({
                    ...apiKeys,
                    tts_api_url: e.target.value
                  })}
                  placeholder="https://api.example.com/tts"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm"
                />
              </div>
            </div>
          </div>

          {/* 图片生成配置 */}
          <div className="pb-4">
            <h3 className="text-md font-medium text-gray-900 mb-3">图片生成服务</h3>
            <div className="space-y-3">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  API Key
                </label>
                <input
                  type="password"
                  value={apiKeys.image_api_key}
                  onChange={(e) => setApiKeys({
                    ...apiKeys,
                    image_api_key: e.target.value
                  })}
                  placeholder="输入图片生成API密钥"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  API URL
                </label>
                <input
                  type="text"
                  value={apiKeys.image_api_url}
                  onChange={(e) => setApiKeys({
                    ...apiKeys,
                    image_api_url: e.target.value
                  })}
                  placeholder="https://api.example.com/image"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm"
                />
              </div>
            </div>
          </div>

          <button
            onClick={handleSaveApiKeys}
            disabled={saving}
            className="px-4 py-2 bg-indigo-600 text-white rounded-lg text-sm font-medium hover:bg-indigo-700 disabled:opacity-50"
          >
            {saving ? '保存中...' : '保存API密钥'}
          </button>
        </div>
      </div>
    </div>
  )
}
