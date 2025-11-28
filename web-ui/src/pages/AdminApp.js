import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, BarElement, Title, Tooltip, Legend } from 'chart.js';
import { Line, Bar } from 'react-chartjs-2';
import '../App.css';

// 注册Chart.js组件
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend
);

function AdminApp() {
  const [marketData, setMarketData] = useState({});
  const [balance, setBalance] = useState({});
  const [positions, setPositions] = useState({});
  const [history, setHistory] = useState([]);
  const [performance, setPerformance] = useState({});
  const [order, setOrder] = useState({ symbol: 'BTC/USDT', side: 'buy', quantity: '' });
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('dashboard');
  const [chartData, setChartData] = useState({});
  const [selectedSymbol, setSelectedSymbol] = useState('BTC/USDT');
  const [timeRange, setTimeRange] = useState('1h');
  const [systemStatus, setSystemStatus] = useState('online');
  const [stats, setStats] = useState({
    totalTrades: 0,
    averageReturn: 0,
    maxDrawdown: 0,
    riskScore: 0,
    winRate: 0,
    totalProfit: 0
  });
  const [symbolStats, setSymbolStats] = useState({});
  const [users, setUsers] = useState([]);
  const [selectedUser, setSelectedUser] = useState(null);
  const [priceHistoryRef, setPriceHistoryRef] = useState({});

  // 定期获取数据
  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 3000);
    return () => clearInterval(interval);
  }, []);

  const fetchData = async () => {
    try {
      // 模拟数据获取
      const mockMarketData = {
        'BTC/USDT': { price: 45000 + Math.random() * 1000, change: (Math.random() - 0.5) * 5, volume: 1000000 },
        'ETH/USDT': { price: 3000 + Math.random() * 100, change: (Math.random() - 0.5) * 5, volume: 2000000 },
        'BNB/USDT': { price: 300 + Math.random() * 20, change: (Math.random() - 0.5) * 5, volume: 500000 },
        'SOL/USDT': { price: 110 + Math.random() * 10, change: (Math.random() - 0.5) * 5, volume: 800000 }
      };

      const mockBalance = {
        total: 15000 + Math.random() * 5000,
        available: 10000 + Math.random() * 2000,
        pnl: (Math.random() - 0.5) * 2000
      };

      const mockPositions = {
        'BTC/USDT': { quantity: 0.1 + Math.random() * 0.2, current_price: mockMarketData['BTC/USDT'].price, value: (0.1 + Math.random() * 0.2) * mockMarketData['BTC/USDT'].price },
        'ETH/USDT': { quantity: 2 + Math.random() * 3, current_price: mockMarketData['ETH/USDT'].price, value: (2 + Math.random() * 3) * mockMarketData['ETH/USDT'].price }
      };

      const mockHistory = [
        { id: 1, symbol: 'BTC/USDT', side: 'buy', quantity: 0.1, price: 44500, total: 4450, datetime: '2023-11-15 10:30:00' },
        { id: 2, symbol: 'ETH/USDT', side: 'buy', quantity: 2, price: 2950, total: 5900, datetime: '2023-11-15 11:45:00' },
        { id: 3, symbol: 'BNB/USDT', side: 'sell', quantity: 10, price: 290, total: 2900, datetime: '2023-11-15 14:20:00' }
      ];

      const mockPerformance = {
        total_trades: 156,
        win_rate: 68.5,
        winning_trades: 107,
        total_volume: 1250000
      };

      const mockStats = {
        totalTrades: 156,
        averageReturn: 0.85,
        maxDrawdown: 12.3,
        riskScore: 7.2,
        winRate: 68.5,
        totalProfit: 8500
      };

      const mockSymbolStats = {
        'BTC/USDT': { volume: 1250000, profit: 5200, winRate: 72.3 },
        'ETH/USDT': { volume: 980000, profit: 2800, winRate: 65.1 },
        'BNB/USDT': { volume: 420000, profit: 500, winRate: 60.5 },
        'SOL/USDT': { volume: 180000, profit: 0, winRate: 55.0 }
      };

      const mockUsers = [
        { id: 1, name: 'User 1', balance: 15000, trades: 45, status: 'active' },
        { id: 2, name: 'User 2', balance: 8500, trades: 28, status: 'active' },
        { id: 3, name: 'User 3', balance: 22000, trades: 63, status: 'active' }
      ];

      setMarketData(mockMarketData);
      setBalance(mockBalance);
      setPositions(mockPositions);
      setHistory(mockHistory);
      setPerformance(mockPerformance);
      setStats(mockStats);
      setSymbolStats(mockSymbolStats);
      setUsers(mockUsers);
      
      // 生成模拟图表数据
      generateChartData(mockMarketData);
    } catch (error) {
      console.error('Error fetching data:', error);
    }
  };

  const generateChartData = (marketData) => {
    // 生成模拟历史价格数据
    const symbols = Object.keys(marketData);
    const times = Array.from({ length: 10 }, (_, i) => `${i * 6}h ago`);
    
    // 为每个交易对生成模拟价格历史
    const newPriceHistory = {};
    symbols.forEach(symbol => {
      newPriceHistory[symbol] = {
        prices: Array.from({ length: 10 }, () => marketData[symbol].price * (0.95 + Math.random() * 0.1)),
        times: times
      };
    });
    
    // 生成统计数据图表
    const newChartData = {
      priceChart: {
        labels: times,
        datasets: symbols.map(symbol => ({
          label: `${symbol} 价格`,
          data: newPriceHistory[symbol].prices,
          borderColor: symbolColors[symbol] || `rgba(${Math.random() * 255}, ${Math.random() * 255}, ${Math.random() * 255}, 1)`,
          backgroundColor: symbolColors[symbol] || `rgba(${Math.random() * 255}, ${Math.random() * 255}, ${Math.random() * 255}, 0.2)`,
          tension: 0.1,
          fill: true
        }))
      },
      performanceChart: {
        labels: symbols,
        datasets: [
          {
            label: '交易量',
            data: symbols.map(symbol => symbolStats[symbol]?.volume || 0),
            backgroundColor: 'rgba(54, 162, 235, 0.6)',
            borderColor: 'rgba(54, 162, 235, 1)',
            borderWidth: 1
          }
        ]
      },
      winRateChart: {
        labels: symbols,
        datasets: [
          {
            label: '胜率 (%)',
            data: symbols.map(symbol => symbolStats[symbol]?.winRate || 0),
            backgroundColor: 'rgba(75, 192, 192, 0.6)',
            borderColor: 'rgba(75, 192, 192, 1)',
            borderWidth: 1
          }
        ]
      }
    };
    
    setChartData(newChartData);
    setPriceHistoryRef(newPriceHistory);
  };

  const placeOrder = async () => {
    if (!order.quantity || parseFloat(order.quantity) <= 0) {
      alert('请输入有效的数量');
      return;
    }

    setLoading(true);
    try {
      // 模拟下单
      await new Promise(resolve => setTimeout(resolve, 1000));
      alert(`订单执行成功! ${order.side === 'buy' ? '买入' : '卖出'} ${order.quantity} ${order.symbol}`);
      setOrder({ ...order, quantity: '' });
      fetchData();
    } catch (error) {
      alert('下单错误: ' + (error.response?.data?.error || error.message));
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (value) => {
    return parseFloat(value || 0).toLocaleString('en-US', {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    });
  };

  const formatNumber = (value, decimals = 4) => {
    return parseFloat(value || 0).toLocaleString('en-US', {
      minimumFractionDigits: decimals,
      maximumFractionDigits: decimals
    });
  };

  // 交易对颜色映射
  const symbolColors = {
    'BTC/USDT': 'rgba(247, 147, 26, 1)',
    'ETH/USDT': 'rgba(79, 42, 231, 1)',
    'BNB/USDT': 'rgba(211, 12, 249, 1)',
    'SOL/USDT': 'rgba(0, 0, 0, 1)'
  };

  return (
    <div className="app admin-app">
      <div className="page-identifier">这是后台管理页面的独特内容</div>
      {/* 顶部导航 */}
      <header className="app-header">
        <div className="header-content">
          <div className="logo">
            <h1>⚙️ ADS Trading Admin</h1>
            <span className="version">v1.0.0</span>
          </div>

          <div className="header-right">
            <div className="system-status">
              <span className={`status-indicator ${systemStatus}`}></span>
              <span>系统状态: {systemStatus === 'online' ? '在线' : '离线'}</span>
            </div>
            <div className="admin-info">
              <span>管理员</span>
            </div>
          </div>
        </div>
      </header>

      {/* 侧边导航 */}
      <aside className="admin-sidebar">
        <nav className="sidebar-nav">
          <button
            className={`nav-item ${activeTab === 'dashboard' ? 'active' : ''}`}
            onClick={() => setActiveTab('dashboard')}
          >
            📊 仪表盘
          </button>
          <button
            className={`nav-item ${activeTab === 'market' ? 'active' : ''}`}
            onClick={() => setActiveTab('market')}
          >
            📈 市场监控
          </button>
          <button
            className={`nav-item ${activeTab === 'trading' ? 'active' : ''}`}
            onClick={() => setActiveTab('trading')}
          >
            💹 交易管理
          </button>
          <button
            className={`nav-item ${activeTab === 'portfolio' ? 'active' : ''}`}
            onClick={() => setActiveTab('portfolio')}
          >
            💼 资产组合
          </button>
          <button
            className={`nav-item ${activeTab === 'history' ? 'active' : ''}`}
            onClick={() => setActiveTab('history')}
          >
            📋 交易历史
          </button>
          <button
            className={`nav-item ${activeTab === 'users' ? 'active' : ''}`}
            onClick={() => setActiveTab('users')}
          >
            👥 用户管理
          </button>
          <button
            className={`nav-item ${activeTab === 'settings' ? 'active' : ''}`}
            onClick={() => setActiveTab('settings')}
          >
            ⚙️ 系统设置
          </button>
        </nav>
      </aside>

      {/* 主内容区域 */}
      <main className="admin-content">
        {/* 仪表盘 */}
        {activeTab === 'dashboard' && (
          <div className="dashboard-section">
            <h2>📊 系统概览</h2>
            
            <div className="stats-grid">
              <div className="stat-card">
                <div className="stat-title">总交易次数</div>
                <div className="stat-value">{stats.totalTrades}</div>
              </div>
              <div className={`stat-card ${stats.averageReturn >= 0 ? 'positive' : 'negative'}`}>
                <div className="stat-title">平均收益率 (%)</div>
                <div className="stat-value">{stats.averageReturn.toFixed(2)}</div>
              </div>
              <div className="stat-card negative">
                <div className="stat-title">最大回撤 (%)</div>
                <div className="stat-value">{stats.maxDrawdown.toFixed(2)}</div>
              </div>
              <div className="stat-card">
                <div className="stat-title">风险评分</div>
                <div className="stat-value">{stats.riskScore.toFixed(1)}</div>
              </div>
              <div className="stat-card positive">
                <div className="stat-title">胜率 (%)</div>
                <div className="stat-value">{stats.winRate}</div>
              </div>
              <div className={`stat-card ${stats.totalProfit >= 0 ? 'positive' : 'negative'}`}>
                <div className="stat-title">总盈利</div>
                <div className="stat-value">${formatCurrency(stats.totalProfit)}</div>
              </div>
            </div>

            <div className="charts-container">
              <div className="chart-card">
                <h3>价格走势</h3>
                <div className="chart-wrapper">
                  {chartData.priceChart && (
                    <Line 
                      data={chartData.priceChart} 
                      options={{
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {
                          legend: { position: 'top' },
                          title: { display: true, text: '主要交易对价格走势' },
                        },
                      }} 
                    />
                  )}
                </div>
              </div>

              <div className="chart-card">
                <h3>交易量分析</h3>
                <div className="chart-wrapper">
                  {chartData.performanceChart && (
                    <Bar 
                      data={chartData.performanceChart} 
                      options={{
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {
                          legend: { position: 'top' },
                          title: { display: true, text: '各交易对交易量' },
                        },
                      }} 
                    />
                  )}
                </div>
              </div>

              <div className="chart-card">
                <h3>胜率分析</h3>
                <div className="chart-wrapper">
                  {chartData.winRateChart && (
                    <Bar 
                      data={chartData.winRateChart} 
                      options={{
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {
                          legend: { position: 'top' },
                          title: { display: true, text: '各交易对胜率' },
                        },
                        scales: {
                          y: {
                            beginAtZero: true,
                            max: 100
                          }
                        }
                      }} 
                    />
                  )}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* 市场监控 */}
        {activeTab === 'market' && (
          <div className="market-section">
            <h2>📈 市场监控</h2>
            <div className="market-grid">
              {Object.entries(marketData).map(([symbol, data]) => (
                <div key={symbol} className={`market-card ${selectedSymbol === symbol ? 'selected' : ''}`} onClick={() => setSelectedSymbol(symbol)}>
                  <div className="symbol">{symbol}</div>
                  <div className="price">${formatCurrency(data.price)}</div>
                  <div className={`change ${data.change >= 0 ? 'positive' : 'negative'}`}>
                    {data.change >= 0 ? '↗' : '↘'} {Math.abs(data.change).toFixed(2)}%
                  </div>
                  <div className="volume">量: {data.volume?.toLocaleString()}</div>
                </div>
              ))}
            </div>
            
            <div className="symbol-stats">
              <h3>📊 {selectedSymbol} 统计</h3>
              {symbolStats[selectedSymbol] && (
                <div className="symbol-stats-grid">
                  <div className="stat-item">
                    <span>交易量</span>
                    <strong>${formatCurrency(symbolStats[selectedSymbol].volume)}</strong>
                  </div>
                  <div className="stat-item">
                    <span>盈利</span>
                    <strong>${formatCurrency(symbolStats[selectedSymbol].profit)}</strong>
                  </div>
                  <div className="stat-item">
                    <span>胜率</span>
                    <strong>{symbolStats[selectedSymbol].winRate}%</strong>
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        {/* 交易管理 */}
        {activeTab === 'trading' && (
          <div className="trading-section">
            <h2>💹 交易管理</h2>
            
            <div className="order-form">
              <h3>创建订单</h3>
              
              <div className="form-group">
                <label>交易对:</label>
                <select
                  value={order.symbol}
                  onChange={(e) => setOrder({...order, symbol: e.target.value})}
                >
                  {Object.keys(marketData).map(symbol => (
                    <option key={symbol} value={symbol}>{symbol}</option>
                  ))}
                </select>
              </div>

              <div className="form-group">
                <label>交易方向:</label>
                <div className="side-buttons">
                  <button
                    className={order.side === 'buy' ? 'active buy' : ''}
                    onClick={() => setOrder({...order, side: 'buy'})}
                  >
                    🟢 买入
                  </button>
                  <button
                    className={order.side === 'sell' ? 'active sell' : ''}
                    onClick={() => setOrder({...order, side: 'sell'})}
                  >
                    🔴 卖出
                  </button>
                </div>
              </div>

              <div className="form-group">
                <label>数量:</label>
                <input
                  type="number"
                  step="0.001"
                  value={order.quantity}
                  onChange={(e) => setOrder({...order, quantity: e.target.value})}
                  placeholder="输入交易数量"
                />
              </div>

              <div className="order-preview">
                {order.quantity && marketData[order.symbol] && (
                  <div className="preview-info">
                    <div>预估金额: <strong>${formatCurrency(marketData[order.symbol].price * order.quantity)}</strong></div>
                    <div>价格: ${formatCurrency(marketData[order.symbol].price)}</div>
                  </div>
                )}
              </div>

              <button
                className={`order-button ${order.side}`}
                onClick={placeOrder}
                disabled={loading || !order.quantity}
              >
                {loading ? '🔄 执行中...' : order.side === 'buy' ? '🟢 买入' : '🔴 卖出'}
              </button>
            </div>
          </div>
        )}

        {/* 资产组合 */}
        {activeTab === 'portfolio' && (
          <div className="portfolio-section">
            <h2>💼 资产组合</h2>
            
            <div className="portfolio-overview">
              <div className="overview-card">
                <h3>资产概览</h3>
                <div className="overview-stats">
                  <div className="overview-item">
                    <span>总资产:</span>
                    <strong>${formatCurrency(balance.total)}</strong>
                  </div>
                  <div className="overview-item">
                    <span>可用资金:</span>
                    <strong>${formatCurrency(balance.available)}</strong>
                  </div>
                  <div className={`overview-item ${balance.pnl >= 0 ? 'positive' : 'negative'}`}>
                    <span>总盈亏:</span>
                    <strong>${formatCurrency(balance.pnl)}</strong>
                  </div>
                </div>
              </div>
            </div>

            <div className="positions-table">
              <h3>当前持仓</h3>
              {Object.keys(positions).length === 0 ? (
                <div className="empty-state">暂无持仓</div>
              ) : (
                <table>
                  <thead>
                    <tr>
                      <th>交易对</th>
                      <th>数量</th>
                      <th>当前价格</th>
                      <th>市值</th>
                    </tr>
                  </thead>
                  <tbody>
                    {Object.entries(positions).map(([symbol, data]) => (
                      <tr key={symbol}>
                        <td>{symbol}</td>
                        <td>{formatNumber(data.quantity)}</td>
                        <td>${formatCurrency(data.current_price)}</td>
                        <td>${formatCurrency(data.value)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              )}
            </div>
          </div>
        )}

        {/* 交易历史 */}
        {activeTab === 'history' && (
          <div className="history-section">
            <h2>📋 交易历史</h2>
            
            <div className="history-table">
              {history.length === 0 ? (
                <div className="empty-state">暂无交易记录</div>
              ) : (
                <table>
                  <thead>
                    <tr>
                      <th>ID</th>
                      <th>交易对</th>
                      <th>方向</th>
                      <th>数量</th>
                      <th>价格</th>
                      <th>总额</th>
                      <th>时间</th>
                    </tr>
                  </thead>
                  <tbody>
                    {history.slice().reverse().map(trade => (
                      <tr key={trade.id} className={`trade-row ${trade.side}`}>
                        <td>{trade.id}</td>
                        <td>{trade.symbol}</td>
                        <td>{trade.side === 'buy' ? '买入' : '卖出'}</td>
                        <td>{formatNumber(trade.quantity)}</td>
                        <td>${formatCurrency(trade.price)}</td>
                        <td>${formatCurrency(trade.total)}</td>
                        <td>{trade.datetime}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              )}
            </div>
          </div>
        )}

        {/* 用户管理 */}
        {activeTab === 'users' && (
          <div className="users-section">
            <h2>👥 用户管理</h2>
            
            <div className="users-grid">
              {users.map(user => (
                <div 
                  key={user.id} 
                  className={`user-card ${selectedUser?.id === user.id ? 'selected' : ''}`}
                  onClick={() => setSelectedUser(user)}
                >
                  <div className="user-info">
                    <h4>{user.name}</h4>
                    <div className="user-balance">余额: ${formatCurrency(user.balance)}</div>
                    <div className="user-trades">交易次数: {user.trades}</div>
                    <div className={`user-status ${user.status}`}>{user.status === 'active' ? '活跃' : '禁用'}</div>
                  </div>
                </div>
              ))}
            </div>
            
            {selectedUser && (
              <div className="user-detail">
                <h3>用户详情: {selectedUser.name}</h3>
                <div className="detail-grid">
                  <div className="detail-item">
                    <span>用户ID</span>
                    <strong>{selectedUser.id}</strong>
                  </div>
                  <div className="detail-item">
                    <span>余额</span>
                    <strong>${formatCurrency(selectedUser.balance)}</strong>
                  </div>
                  <div className="detail-item">
                    <span>交易次数</span>
                    <strong>{selectedUser.trades}</strong>
                  </div>
                  <div className="detail-item">
                    <span>状态</span>
                    <strong>{selectedUser.status === 'active' ? '活跃' : '禁用'}</strong>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}

        {/* 系统设置 */}
        {activeTab === 'settings' && (
          <div className="settings-section">
            <h2>⚙️ 系统设置</h2>
            
            <div className="settings-grid">
              <div className="settings-card">
                <h3>系统配置</h3>
                <div className="setting-item">
                  <label>系统状态</label>
                  <div className="setting-value">
                    <span className={`status-indicator ${systemStatus}`}></span>
                    <span>{systemStatus === 'online' ? '在线' : '离线'}</span>
                  </div>
                </div>
                <div className="setting-item">
                  <label>自动交易</label>
                  <div className="setting-value">
                    <input type="checkbox" defaultChecked={true} />
                    <span>启用</span>
                  </div>
                </div>
                <div className="setting-item">
                  <label>风险控制</label>
                  <div className="setting-value">
                    <select defaultValue="medium">
                      <option value="low">低风险</option>
                      <option value="medium">中风险</option>
                      <option value="high">高风险</option>
                    </select>
                  </div>
                </div>
              </div>

              <div className="settings-card">
                <h3>通知设置</h3>
                <div className="setting-item">
                  <label>邮件通知</label>
                  <div className="setting-value">
                    <input type="checkbox" defaultChecked={true} />
                    <span>启用</span>
                  </div>
                </div>
                <div className="setting-item">
                  <label>短信通知</label>
                  <div className="setting-value">
                    <input type="checkbox" defaultChecked={false} />
                    <span>禁用</span>
                  </div>
                </div>
                <div className="setting-item">
                  <label>警报阈值</label>
                  <div className="setting-value">
                    <input type="number" defaultValue="5" min="1" max="20" />
                    <span>%</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </main>

      <footer className="app-footer">
        <p>ADS Trading System - 管理后台 v1.0.0</p>
      </footer>
    </div>
  );
}

export default AdminApp;