import './Billing.css'

export default function Billing() {
  return (
    <div className="page">
      <h1 className="page-title">消费记录</h1>

      <div className="card">
        <table className="table">
          <thead>
            <tr>
              <th>时间</th>
              <th>任务</th>
              <th>类型</th>
              <th>数量</th>
              <th>金额</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>2026-04-01</td>
              <td>《龙族传说》</td>
              <td>小说生成</td>
              <td>32万字</td>
              <td>-¥25.60</td>
            </tr>
            <tr>
              <td>2026-04-01</td>
              <td>龙族传说·视频</td>
              <td>视频制作</td>
              <td>36分钟</td>
              <td>-¥324.00</td>
            </tr>
            <tr>
              <td>2026-03-30</td>
              <td>充值</td>
              <td>微信支付</td>
              <td>-</td>
              <td style={{ color: '#22c55e' }}>+¥500.00</td>
            </tr>
            <tr>
              <td>2026-03-28</td>
              <td>《霸总的秘密》</td>
              <td>小说生成</td>
              <td>2.8万字</td>
              <td>-¥2.24</td>
            </tr>
            <tr>
              <td>2026-03-25</td>
              <td>AI峰会速览</td>
              <td>资讯视频</td>
              <td>2.5分钟</td>
              <td>-¥22.50</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  )
}
