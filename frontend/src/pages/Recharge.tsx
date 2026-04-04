import { useState } from 'react'
import './Recharge.css'

export default function Recharge() {
  const [amount, setAmount] = useState(100)
  const [method, setMethod] = useState('wechat')

  return (
    <div className="page">
      <h1 className="page-title">充值</h1>

      <div className="card">
        <h2>当前余额</h2>
        <div className="balance-display">¥ 88.30</div>
      </div>

      <div className="card">
        <h2>选择充值金额</h2>
        <div className="options">
          {[50, 100, 200, 500, 1000].map(val => (
            <div key={val} className={`option ${amount === val ? 'selected' : ''}`} onClick={() => setAmount(val)}>
              ¥{val}
            </div>
          ))}
          <div className="option">自定义</div>
        </div>

        <h2 style={{ marginTop: '24px' }}>支付方式</h2>
        <div className="options">
          <div className={`option ${method === 'wechat' ? 'selected' : ''}`} onClick={() => setMethod('wechat')}>
            💚 微信支付
          </div>
          <div className={`option ${method === 'alipay' ? 'selected' : ''}`} onClick={() => setMethod('alipay')}>
            🔵 支付宝
          </div>
        </div>

        <button className="btn btn-primary">确认充值 ¥{amount}</button>
      </div>
    </div>
  )
}
