import React, { useState, useEffect } from 'react';
import '../App.css';

function MobileApp() {
  // 状态管理
  const [totalAsset, setTotalAsset] = useState(0.47059694);
  const [todayPnl, setTodayPnl] = useState(0.0025204);
  const [todayPnlPercent, setTodayPnlPercent] = useState(0.54);
  const [balances, setBalances] = useState({
    spot: 0.32239252,
    funding: 0.08572,
    alpha: 0.06248442,
    contract: 0.0,
    robot: 0.0
  });
  const [activeNav, setActiveNav] = useState('asset');
  const [activeTab, setActiveTab] = useState('overview');

  // 模拟时间更新
  const [currentTime, setCurrentTime] = useState(new Date());
  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentTime(new Date());
    }, 1000);
    return () => clearInterval(timer);
  }, []);

  // 格式化时间
  const formatTime = (date) => {
    const hours = String(date.getHours()).padStart(2, '0');
    const minutes = String(date.getMinutes()).padStart(2, '0');
    return `${hours}:${minutes}`;
  };

  // 资产类型配置
  const assetTypes = [
    { key: 'spot', name: '现货', balance: balances.spot, unit: 'USDT', color: '#28a745' },
    { key: 'funding', name: '资金', balance: balances.funding, unit: 'USDT', color: '#17a2b8' },
    { key: 'alpha', name: 'Alpha', balance: balances.alpha, unit: 'USDT', color: '#ffc107' },
    { key: 'contract', name: '合约', balance: balances.contract, unit: 'USDT', color: '#dc3545' },
    { key: 'robot', name: '交易机器人', balance: balances.robot, unit: 'USDT', color: '#6f42c1' }
  ];

  // 底部导航配置
  const bottomNav = [
    { key: 'home', name: '首页', icon: '🏠' },
    { key: 'market', name: '行情', icon: '📈' },
    { key: 'trade', name: '交易', icon: '🔄' },
    { key: 'contract', name: '合约', icon: '📝' },
    { key: 'asset', name: '资产', icon: '💰' }
  ];

  // 顶部导航配置
  const topTabs = [
    { key: 'overview', name: '总览' },
    { key: 'spot', name: '现货' },
    { key: 'funding', name: '资金' },
    { key: 'alpha', name: 'Alpha' },
    { key: 'contract', name: '合约' }
  ];

  return (
    <div className="mobile-app-container">
      {/* 顶部状态栏 */}
      <div className="mobile-status-bar">
        <div className="status-left">
          <span className="status-time">{formatTime(currentTime)}</span>
        </div>
        <div className="status-right">
          <span className="status-icon">📶</span>
          <span className="status-icon">📱</span>
          <span className="status-icon">🔋</span>
        </div>
      </div>

      {/* 主内容区域 */}
      <div className="mobile-main-content">
        {/* 顶部导航 */}
        <div className="mobile-top-tabs">
          {topTabs.map(tab => (
            <div
              key={tab.key}
              className={`top-tab ${activeTab === tab.key ? 'active' : ''}`}
              onClick={() => setActiveTab(tab.key)}
            >
              {tab.name}
            </div>
          ))}
        </div>

        {/* 总资产信息 */}
        <div className="mobile-asset-overview">
          <div className="asset-total">
            <div className="asset-label">预估总资产</div>
            <div className="asset-value">
              <span className="value-number">{totalAsset.toFixed(8)}</span>
              <span className="value-currency"> USDT</span>
            </div>
          </div>
          <div className="asset-pnl">
            <span className="pnl-icon">📈</span>
            <span className="pnl-value positive">+{todayPnl.toFixed(8)} USDT</span>
            <span className="pnl-percent positive">(+{todayPnlPercent}%)</span>
          </div>
        </div>

        {/* 操作按钮 */}
        <div className="mobile-action-buttons">
          <button className="action-btn primary">添加资金</button>
          <button className="action-btn secondary">转出</button>
          <button className="action-btn secondary">划转</button>
        </div>

        {/* 资产分布 */}
        <div className="mobile-asset-distribution">
          <div className="distribution-header">
            <div className="header-left">
              <span className="header-label">币种</span>
              <span className="header-label">账户</span>
            </div>
            <div className="header-right">
              <span className="header-icon">⚙️</span>
            </div>
          </div>

          <div className="distribution-list">
            {assetTypes.map(asset => (
              <div key={asset.key} className="distribution-item">
                <div className="item-left">
                  <span className="item-name">{asset.name}</span>
                  <span className="item-type">{asset.unit}</span>
                </div>
                <div className="item-right">
                  <span className="item-balance">{asset.balance.toFixed(8)}</span>
                  {asset.balance > 0 && (
                    <span className="item-convert">
                      ≈¥{(asset.balance * 7).toFixed(6)} {/* 简单汇率转换模拟 */}
                    </span>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* 底部导航 */}
      <div className="mobile-bottom-nav">
        {bottomNav.map(nav => (
          <div
            key={nav.key}
            className={`bottom-nav-item ${activeNav === nav.key ? 'active' : ''}`}
            onClick={() => setActiveNav(nav.key)}
          >
            <div className="nav-icon">{nav.icon}</div>
            <div className="nav-name">{nav.name}</div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default MobileApp;