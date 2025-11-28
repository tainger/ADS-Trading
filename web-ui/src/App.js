import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import './App.css';
import { Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend } from 'chart.js';
import { Line } from 'react-chartjs-2';

// 注册Chart.js组件
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

function App() {
  const [marketData, setMarketData] = useState({});
  const [balance, setBalance] = useState({});
  const [positions, setPositions] = useState({});
  const [history, setHistory] = useState([]);
  const [performance, setPerformance] = useState({});
  const [order, setOrder] = useState({ symbol: 'BTC/USDT', side: 'buy', quantity: '' });
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('trading');
  const [chartData, setChartData] = useState({});
  const [selectedSymbol, setSelectedSymbol] = useState('BTC/USDT');
  const [timeRange, setTimeRange] = useState('1h');
  const chartRef = useRef(null);
  const priceHistoryRef = useRef({}); // 用于存储价格历史数据

  // 初始化价格历史数据
  useEffect(() => {
    Object.keys(marketData).forEach(symbol => {
      if (!priceHistoryRef.current[symbol]) {
        priceHistoryRef.current[symbol] = { prices: [], times: [] };
      }
    });
  }, [marketData]);

  // 定期获取数据
  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 3000);
    return () => clearInterval(interval);
  }, []);

  const fetchData = async () => {
    try {
      const [marketRes, balanceRes, positionsRes, historyRes, performanceRes] = await Promise.all([
        axios.get('/api/market'),
        axios.get('/api/balance'),
        axios.get('/api/positions'),
        axios.get('/api/history'),
        axios.get('/api/performance')
      ]);

      setMarketData(marketRes.data);
      setBalance(balanceRes.data);
      setPositions(positionsRes.data);
      setHistory(historyRes.data);
      setPerformance(performanceRes.data);
      
      // 更新价格历史数据
      updatePriceHistory(marketRes.data);
    } catch (error) {
      console.error('Error fetching data:', error);
    }
  };

  const updatePriceHistory = (marketData) => {
    const now = new Date();
    const timeLabel = now.toLocaleTimeString();
    
    Object.entries(marketData).forEach(([symbol, data]) => {
      if (!priceHistoryRef.current[symbol]) {
        priceHistoryRef.current[symbol] = { prices: [], times: [] };
      }
      
      // 添加新的价格数据
      priceHistoryRef.current[symbol].prices.push(data.price);
      priceHistoryRef.current[symbol].times.push(timeLabel);
      
      // 限制数据点数量（保留最近30个数据点）
      if (priceHistoryRef.current[symbol].prices.length > 30) {
        priceHistoryRef.current[symbol].prices.shift();
        priceHistoryRef.current[symbol].times.shift();
      }
    });
    
    // 更新图表数据
    updateChart(selectedSymbol);
  };

  const updateChart = (symbol) => {
    if (!priceHistoryRef.current[symbol]) {
      priceHistoryRef.current[symbol] = { prices: [], times: [] };
    }
    
    const data = {
      labels: priceHistoryRef.current[symbol].times,
      datasets: [
        {
          label: `${symbol} 价格`,
          data: priceHistoryRef.current[symbol].prices,
          borderColor: 'rgba(75, 192, 192, 1)',
          backgroundColor: 'rgba(75, 192, 192, 0.2)',
          tension: 0.1,
          fill: true
        },
      ],
    };
    
    setChartData(data);
  };
  
  // 当选择的交易对改变时更新图表
  useEffect(() => {
    updateChart(selectedSymbol);
  }, [selectedSymbol]);

  const placeOrder = async () => {
    if (!order.quantity || parseFloat(order.quantity) <= 0) {
      alert('请输入有效的数量');
      return;
    }

    setLoading(true);
    try {
      const response = await axios.post('/api/order', {
        symbol: order.symbol,
        side: order.side,
        quantity: parseFloat(order.quantity)
      });

      if (response.data.success) {
        alert(`订单执行成功! ${order.side === 'buy' ? '买入' : '卖出'} ${order.quantity} ${order.symbol}`);
        setOrder({ ...order, quantity: '' });
        fetchData();
      } else {
        alert('订单失败: ' + response.data.error);
      }
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

  return (
    <div className="app">
      {/* 顶部导航 */}
      <header className="app-header">
        <div className="header-content">
          <div className="logo">
            <h1>🚀 ADS Trading</h1>
            <span className="version">v1.0.0</span>
          </div>

          <div className="balance-info">
            <div className="balance-item">
              <span>总资产:</span>
              <strong>${formatCurrency(balance.total)}</strong>
            </div>
            <div className="balance-item">
              <span>可用资金:</span>
              <strong>${formatCurrency(balance.available)}</strong>
            </div>
            <div className={`balance-item ${balance.pnl >= 0 ? 'positive' : 'negative'}`}>
              <span>盈亏:</span>
              <strong>${formatCurrency(balance.pnl)}</strong>
            </div>
          </div>

          {/* 桌面端导航 */}
          <nav className="nav-tabs desktop-nav">
            <button
              className={activeTab === 'trading' ? 'active' : ''}
              onClick={() => setActiveTab('trading')}
            >
              📊 交易
            </button>
            <button
              className={activeTab === 'portfolio' ? 'active' : ''}
              onClick={() => setActiveTab('portfolio')}
            >
              💼 持仓
            </button>
            <button
              className={activeTab === 'history' ? 'active' : ''}
              onClick={() => setActiveTab('history')}
            >
              📈 历史
            </button>
            <button
              className={activeTab === 'performance' ? 'active' : ''}
              onClick={() => setActiveTab('performance')}
            >
              🎯 表现
            </button>
          </nav>
        </div>
      </header>

      <div className="app-content">
        {/* 移动端专用收益概览组件 */}
        <div className="mobile-performance-overview">
          <div className="overview-card">
            <h3>📊 策略收益</h3>
            <div className="overview-stats">
              <div className="overview-item">
                <span>总资产</span>
                <strong>${formatCurrency(balance.total)}</strong>
              </div>
              <div className="overview-item">
                <span>收益率</span>
                <strong className={balance.pnl >= 0 ? 'positive' : 'negative'}>
                  {balance.total > 0 ? ((balance.pnl / (balance.total - balance.pnl)) * 100).toFixed(2) : 0}%
                </strong>
              </div>
              <div className={`overview-item ${balance.pnl >= 0 ? 'positive' : 'negative'}`}>
                <span>总盈亏</span>
                <strong>${formatCurrency(balance.pnl)}</strong>
              </div>
              <div className="overview-item">
                <span>交易次数</span>
                <strong>{performance.total_trades || 0}</strong>
              </div>
            </div>
          </div>
        </div>
        
        {/* 市场数据概览和图表 */}
        <section className="market-section">
          <div className="market-overview">
            <h2>实时行情</h2>
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
          </div>
          
          {/* 价格走势图 */}
          <div className="chart-section">
            <div className="chart-header">
              <h2>{selectedSymbol} 价格走势</h2>
              <div className="chart-controls">
                <select value={timeRange} onChange={(e) => setTimeRange(e.target.value)}>
                  <option value="1h">1小时</option>
                  <option value="4h">4小时</option>
                  <option value="1d">1天</option>
                </select>
              </div>
            </div>
            <div className="chart-container">
              {Object.keys(chartData).length > 0 && (
                <Line 
                  ref={chartRef}
                  data={chartData} 
                  options={{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                      legend: {
                        position: window.innerWidth <= 768 ? 'top' : 'top',
                        labels: {
                          // 在移动设备上使用更小的字体
                          font: {
                            size: window.innerWidth <= 768 ? 12 : 14
                          }
                        }
                      },
                      tooltip: {
                        mode: window.innerWidth <= 768 ? 'nearest' : 'index',
                        intersect: false,
                        callbacks: {
                          label: function(context) {
                            return `${context.dataset.label}: $${formatCurrency(context.parsed.y)}`;
                          }
                        }
                      },
                      title: {
                        // 移动设备上隐藏标题
                        display: window.innerWidth > 768
                      }
                    },
                    scales: {
                      y: {
                        beginAtZero: false,
                        ticks: {
                          callback: function(value) {
                            return '$' + formatCurrency(value);
                          },
                          // 移动设备上减少刻度数量
                          maxTicksLimit: window.innerWidth <= 768 ? 4 : 6
                        }
                      },
                      x: {
                        ticks: {
                          maxRotation: window.innerWidth <= 768 ? 0 : 45,
                          minRotation: window.innerWidth <= 768 ? 0 : 45,
                          // 移动设备上减少标签数量
                          maxTicksLimit: window.innerWidth <= 768 ? 5 : 10
                        }
                      }
                    },
                    // 优化移动设备的触摸交互
                    interaction: {
                      intersect: false,
                      mode: window.innerWidth <= 768 ? 'nearest' : 'index'
                    },
                    // 移动设备上减少数据点数量
                    elements: {
                      point: {
                        radius: window.innerWidth <= 768 ? 2 : 4,
                        hoverRadius: window.innerWidth <= 768 ? 4 : 6
                      },
                      line: {
                        borderWidth: window.innerWidth <= 768 ? 2 : 3
                      }
                    }
                  }} 
                />
              )}
            </div>
          </div>
        </section>

        {/* 主要内容区域 */}
        <div className="main-content">
          {/* 交易面板 */}
          {activeTab === 'trading' && (
            <section className="trading-section">
              <div className="trading-card">
                <h3>快速交易</h3>

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
            </section>
          )}

          {/* 持仓面板 */}
          {activeTab === 'portfolio' && (
            <section className="portfolio-section">
              <div className="portfolio-card">
                <h3>当前持仓</h3>
                {Object.keys(positions).length === 0 ? (
                  <div className="empty-state">暂无持仓</div>
                ) : (
                  <div className="positions-table">
                    <div className="table-header">
                      <span>交易对</span>
                      <span>数量</span>
                      <span>当前价格</span>
                      <span>市值</span>
                    </div>
                    {Object.entries(positions).map(([symbol, data]) => (
                      <div key={symbol} className="table-row">
                        <span className="symbol">{symbol}</span>
                        <span className="quantity">{formatNumber(data.quantity)}</span>
                        <span className="price">${formatCurrency(data.current_price)}</span>
                        <span className="value">${formatCurrency(data.value)}</span>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </section>
          )}

          {/* 历史记录 */}
          {activeTab === 'history' && (
            <section className="history-section">
              <div className="history-card">
                <h3>交易历史</h3>
                {history.length === 0 ? (
                  <div className="empty-state">暂无交易记录</div>
                ) : (
                  <div className="history-list">
                    {history.slice().reverse().map(trade => (
                      <div key={trade.id} className={`history-item ${trade.side}`}>
                        <div className="trade-main">
                          <span className="symbol">{trade.symbol}</span>
                          <span className={`side ${trade.side}`}>
                            {trade.side === 'buy' ? '🟢 买入' : '🔴 卖出'}
                          </span>
                          <span className="quantity">{formatNumber(trade.quantity)}</span>
                        </div>
                        <div className="trade-details">
                          <span>价格: ${formatCurrency(trade.price)}</span>
                          <span>总额: ${formatCurrency(trade.total)}</span>
                          <span className="time">{trade.datetime}</span>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </section>
          )}

          {/* 表现统计 */}
          {activeTab === 'performance' && (
            <section className="performance-section">
              <div className="performance-card">
                <h3>交易表现</h3>
                <div className="stats-grid">
                  <div className="stat-card">
                    <div className="stat-value">{performance.total_trades || 0}</div>
                    <div className="stat-label">总交易次数</div>
                  </div>
                  <div className="stat-card">
                    <div className="stat-value">{performance.win_rate || 0}%</div>
                    <div className="stat-label">胜率</div>
                  </div>
                  <div className="stat-card">
                    <div className="stat-value">{performance.winning_trades || 0}</div>
                    <div className="stat-label">盈利交易</div>
                  </div>
                  <div className="stat-card">
                    <div className="stat-value">${formatCurrency(performance.total_volume)}</div>
                    <div className="stat-label">总交易额</div>
                  </div>
                </div>
              </div>
            </section>
          )}
        </div>
      </div>

      {/* 移动端底部导航 */}
      <nav className="mobile-nav">
        <button
          className={activeTab === 'trading' ? 'active' : ''}
          onClick={() => setActiveTab('trading')}
        >
          <span className="nav-icon">📊</span>
          <span className="nav-text">交易</span>
        </button>
        <button
          className={activeTab === 'portfolio' ? 'active' : ''}
          onClick={() => setActiveTab('portfolio')}
        >
          <span className="nav-icon">💼</span>
          <span className="nav-text">持仓</span>
        </button>
        <button
          className={activeTab === 'history' ? 'active' : ''}
          onClick={() => setActiveTab('history')}
        >
          <span className="nav-icon">📈</span>
          <span className="nav-text">历史</span>
        </button>
        <button
          className={activeTab === 'performance' ? 'active' : ''}
          onClick={() => setActiveTab('performance')}
        >
          <span className="nav-icon">🎯</span>
          <span className="nav-text">表现</span>
        </button>
      </nav>

      <footer className="app-footer">
        <p>ADS Trading System - 嵌入式 Python + React 架构演示</p>
      </footer>
    </div>
  );
}

export default App;