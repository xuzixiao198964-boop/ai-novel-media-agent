import { useEffect, useState } from 'react'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts'
import { financeApi } from '../api'

export default function Finance() {
  const [summary, setSummary] = useState<any>(null)
  const [trend, setTrend] = useState<any[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadData()
  }, [])

  const loadData = async () => {
    try {
      const [summaryData, trendData] = await Promise.all([
        financeApi.getSummary(),
        financeApi.getTrend(30),
      ]) as unknown as [any, any[]]
      setSummary(summaryData)
      setTrend(trendData)
    } catch (error) {
      console.error('加载财务数据失败:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return <div className="text-center py-12">加载中...</div>
  }

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">财务报表</h1>

      {/* 统计卡片 */}
      <div className="grid grid-cols-4 gap-4 mb-6">
        <div className="bg-white rounded-xl p-5 border border-gray-200">
          <div className="text-xs text-gray-500 mb-1">本月总收入</div>
          <div className="text-3xl font-bold text-green-600">
            ¥{summary?.month_income?.toFixed(2) || '0.00'}
          </div>
        </div>

        <div className="bg-white rounded-xl p-5 border border-gray-200">
          <div className="text-xs text-gray-500 mb-1">本月 API 成本</div>
          <div className="text-3xl font-bold text-red-600">
            ¥{summary?.api_cost?.toFixed(2) || '0.00'}
          </div>
        </div>

        <div className="bg-white rounded-xl p-5 border border-gray-200">
          <div className="text-xs text-gray-500 mb-1">本月毛利</div>
          <div className="text-3xl font-bold text-indigo-600">
            ¥{summary?.gross_profit?.toFixed(2) || '0.00'}
          </div>
        </div>

        <div className="bg-white rounded-xl p-5 border border-gray-200">
          <div className="text-xs text-gray-500 mb-1">毛利率</div>
          <div className="text-3xl font-bold">
            {summary?.profit_margin?.toFixed(1) || '0.0'}%
          </div>
        </div>
      </div>

      {/* 趋势图 */}
      <div className="bg-white rounded-xl p-6 border border-gray-200 mb-4">
        <h2 className="text-lg font-semibold mb-4">收入 vs 成本趋势</h2>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={trend}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="date" tick={{ fontSize: 12 }} />
            <YAxis tick={{ fontSize: 12 }} />
            <Tooltip />
            <Legend />
            <Line type="monotone" dataKey="income" stroke="#22c55e" strokeWidth={2} name="收入" />
            <Line type="monotone" dataKey="cost" stroke="#ef4444" strokeWidth={2} name="成本" />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}
