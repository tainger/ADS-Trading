import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import './App.css';
import MobileApp from './pages/MobileApp';
import AdminApp from './pages/AdminApp';
import TradingApp from './pages/TradingApp';

function App() {
  // 创建带有明显标识的页面组件
  const TradingAppWithId = () => (
    <div className="page-container trading-page">
      <h1 className="page-title">📊 交易页面 - 专属交易功能</h1>
      <div className="unique-feature trading-feature">
        <h2>交易功能</h2>
        <p>这是交易页面，提供完整的交易功能和实时市场数据。</p>
      </div>
      <TradingApp />
    </div>
  );

  const MobileAppWithId = () => (
    <div className="page-container mobile-page">
      <h1 className="page-title">📱 移动端页面 - 移动优化体验</h1>
      <div className="unique-feature mobile-feature">
        <h2>移动端功能</h2>
        <p>这是移动端页面，专为移动设备优化的交易界面。</p>
      </div>
      <MobileApp />
    </div>
  );

  const AdminAppWithId = () => (
    <div className="page-container admin-page">
      <h1 className="page-title">⚙️ 后台管理页面 - 系统管理功能</h1>
      <div className="unique-feature admin-feature">
        <h2>管理功能</h2>
        <p>这是后台管理页面，提供系统监控和管理功能。</p>
      </div>
      <AdminApp />
    </div>
  );

  // 添加导航页面
  const NavigationPage = () => (
    <div className="navigation-container">
      <h1>ADS Trading 系统</h1>
      <div className="navigation-links">
        <Link to="/trading" className="nav-link">
          📊 交易页面
        </Link>
        <Link to="/mobile" className="nav-link">
          📱 移动端页面
        </Link>
        <Link to="/admin" className="nav-link">
          ⚙️ 后台管理页面
        </Link>
      </div>
    </div>
  );

  return (
    <Router>
      <Routes>
        {/* 导航页面 */}
        <Route path="/" element={<NavigationPage />} />
        
        {/* 交易页面 */}
        <Route path="/trading" element={<TradingAppWithId />} />
        
        {/* 移动端页面 */}
        <Route path="/mobile" element={<MobileAppWithId />} />
        
        {/* 后台管理页面 */}
        <Route path="/admin" element={<AdminAppWithId />} />
      </Routes>
    </Router>
  );
}

export default App;
