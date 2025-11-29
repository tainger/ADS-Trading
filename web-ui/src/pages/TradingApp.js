import React, { useState, useEffect, useRef } from 'react';
import { Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend } from 'chart.js';
import { Line } from 'react-chartjs-2';
import '../App.css';

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

function TradingApp() {
  // 交易页面专属状态
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

      setMarketData(mockMarketData);
      setBalance(mockBalance);
      setPositions(mockPositions);
      setHistory(mockHistory);
      setPerformance(mockPerformance);
      
      // 更新价格历史数据
      updatePriceHistory(mockMarketData);
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

  return (
    <div className="app trading-app">
      <div className="page-identifier">这是交易页面的独特内容</div>
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
        </div>
      </header>

      <div className="app-content">
        {/* 市场数据概览 */}
        <section className="market-section">
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
        </section>

        {/* 主要内容区域 */}
        <div className="main-content">
          {/* 左侧交易面板 */}
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

          {/* 右侧图表和信息 */}
          <section className="chart-section">
            <div className="chart-card">
              <div className="chart-header">
                <h3>{selectedSymbol} 价格走势</h3>
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
                          position: 'top',
                        },
                        tooltip: {
                          mode: 'index',
                          intersect: false,
                          callbacks: {
                            label: function(context) {
                              return `${context.dataset.label}: $${formatCurrency(context.parsed.y)}`;
                            }
                          }
                        },
                        title: {
                          display: true,
                          text: `${selectedSymbol} 价格走势 (${timeRange})`
                        },
                      },
                      scales: {
                        y: {
                          beginAtZero: false,
                          ticks: {
                            callback: function(value) {
                              return '$' + formatCurrency(value);
                            }
                          }
                        },
                        x: {
                          ticks: {
                            maxRotation: 45,
                            minRotation: 45
                          }
                        }
                      },
                      interaction: {
                        mode: 'nearest',
                        axis: 'x',
                        intersect: false
                      }
                    }}
                  />
                )}
              </div>
            </div>

            {/* 表现统计 */}
            <div className="stats-card">
              <h3>📊 策略表现</h3>
              <div className="stats-grid">
                <div className="stat-item">
                  <span>总交易次数</span>
                  <strong>{performance.total_trades}</strong>
                </div>
                <div className="stat-item">
                  <span>胜率</span>
                  <strong>{performance.win_rate}%</strong>
                </div>
                <div className="stat-item">
                  <span>盈利交易</span>
                  <strong>{performance.winning_trades}</strong>
                </div>
                <div className="stat-item">
                  <span>总交易额</span>
                  <strong>${formatCurrency(performance.total_volume)}</strong>
                </div>
              </div>
            </div>
          </section>
        </div>

        {/* 底部内容 */}
        <div className="bottom-content">
          {/* 持仓 */}
          <section className="positions-section">
            <div className="positions-card">
              <h3>📈 当前持仓</h3>
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

          {/* 交易历史 */}
          <section className="history-section">
            <div className="history-card">
              <h3>📋 交易历史</h3>
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
        </div>
      </div>

      <footer className="app-footer">
        <p>ADS Trading System - 嵌入式 Python + React 架构演示</p>
      </footer>
    </div>
  );
}

export default TradingApp;