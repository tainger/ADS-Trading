import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css';

function App() {
  const [marketData, setMarketData] = useState({});
  const [balance, setBalance] = useState({});
  const [positions, setPositions] = useState({});
  const [history, setHistory] = useState([]);
  const [performance, setPerformance] = useState({});
  const [order, setOrder] = useState({ symbol: 'BTC/USDT', side: 'buy', quantity: '' });
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('trading');

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
    } catch (error) {
      console.error('Error fetching data:', error);
    }
  };

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

          <nav className="nav-tabs">
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
        {/* 市场数据概览 */}
        <section className="market-overview">
          <h2>实时行情</h2>
          <div className="market-grid">
            {Object.entries(marketData).map(([symbol, data]) => (
              <div key={symbol} className="market-card">
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

      <footer className="app-footer">
        <p>ADS Trading System - 嵌入式 Python + React 架构演示</p>
      </footer>
    </div>
  );
}

export default App;