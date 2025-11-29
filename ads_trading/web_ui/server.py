import os
import json
import time
from flask import Flask, send_from_directory, jsonify, request
from threading import Thread, Lock
import random
from ads_trading.trader.gateway.binance_gateway import BinanceGateway, BinanceGatewayConfig


class TradingEngine:
    """模拟交易引擎"""

    def __init__(self):
        self.balance = 10000.0
        self.positions = {}
        self.trade_history = []
        self.market_data = {
            'BTC/USDT': {'price': 45000.0, 'change': 2.5, 'volume': 28492},
            'ETH/USDT': {'price': 2500.0, 'change': -1.2, 'volume': 15932},
            'ADA/USDT': {'price': 0.45, 'change': 0.8, 'volume': 8921},
            'DOT/USDT': {'price': 6.5, 'change': 3.1, 'volume': 4532},
            'SOL/USDT': {'price': 120.5, 'change': 5.2, 'volume': 12345}
        }
        self.lock = Lock()
        self.running = True

        # 启动市场数据更新线程
        self.update_thread = Thread(target=self._update_market_data, daemon=True)
        self.update_thread.start()

    def _update_market_data(self):
        """模拟市场数据更新"""
        while self.running:
            time.sleep(3)  # 每3秒更新一次
            with self.lock:
                for symbol in self.market_data:
                    # 模拟价格波动
                    change = random.uniform(-2.0, 2.0)
                    current_price = self.market_data[symbol]['price']
                    new_price = max(0.01, current_price * (1 + change / 100))

                    # 更新数据
                    self.market_data[symbol]['price'] = round(new_price, 2)
                    self.market_data[symbol]['change'] = round(change, 2)
                    self.market_data[symbol]['volume'] = random.randint(1000, 30000)

    def get_market_data(self):
        """获取市场数据"""
        with self.lock:
            return self.market_data.copy()

    def get_balance(self):
        """获取账户余额"""
        total_balance = self.balance
        # 计算持仓价值
        for symbol, quantity in self.positions.items():
            if symbol in self.market_data:
                price = self.market_data[symbol]['price']
                total_balance += price * quantity

        return {
            'total': round(total_balance, 2),
            'available': round(self.balance, 2),
            'currency': 'USDT',
            'pnl': round(total_balance - 10000, 2)  # 初始资金10000
        }

    def place_order(self, symbol, side, quantity, order_type='market'):
        """下单"""
        with self.lock:
            if symbol not in self.market_data:
                return {'error': 'Invalid symbol'}

            price = self.market_data[symbol]['price']
            total_cost = price * quantity

            if side == 'buy' and total_cost > self.balance:
                return {'error': 'Insufficient balance'}

            if side == 'sell':
                if symbol not in self.positions or self.positions[symbol] < quantity:
                    return {'error': 'Insufficient position'}

            # 执行交易
            if side == 'buy':
                self.balance -= total_cost
                if symbol in self.positions:
                    self.positions[symbol] += quantity
                else:
                    self.positions[symbol] = quantity
            else:  # sell
                self.positions[symbol] -= quantity
                self.balance += total_cost
                if self.positions[symbol] == 0:
                    del self.positions[symbol]

            # 记录交易历史
            trade = {
                'id': len(self.trade_history) + 1,
                'symbol': symbol,
                'side': side,
                'quantity': quantity,
                'price': price,
                'total': round(total_cost, 2),
                'timestamp': time.time(),
                'datetime': time.strftime('%Y-%m-%d %H:%M:%S')
            }
            self.trade_history.append(trade)

            return {'success': True, 'trade': trade}

    def get_positions(self):
        """获取持仓"""
        positions_with_value = {}
        with self.lock:
            for symbol, quantity in self.positions.items():
                if symbol in self.market_data:
                    price = self.market_data[symbol]['price']
                    positions_with_value[symbol] = {
                        'quantity': quantity,
                        'current_price': price,
                        'value': round(price * quantity, 2)
                    }
        return positions_with_value

    def get_trade_history(self):
        """获取交易历史"""
        return self.trade_history[-20:]  # 返回最近20条记录

    def get_performance(self):
        """获取性能指标"""
        total_trades = len(self.trade_history)
        winning_trades = len([t for t in self.trade_history if t.get('profit', 0) > 0])

        return {
            'total_trades': total_trades,
            'winning_trades': winning_trades,
            'win_rate': round(winning_trades / total_trades * 100, 2) if total_trades > 0 else 0,
            'total_volume': round(sum(t['total'] for t in self.trade_history), 2)
        }
    
    def get_binance_account(self):
        """获取币安账户数据"""
        try:
            # 从配置文件加载币安API密钥和密钥
            from ads_trading.trader.setting import SETTINGS
            
            binance_api_key = SETTINGS.get("binance.api_key", "")
            binance_api_secret = SETTINGS.get("binance.api_secret", "")
            
            if not binance_api_key or not binance_api_secret:
                return {
                    "success": False,
                    "error": "币安API密钥或密钥未配置"
                }
            
            # 创建币安网关配置
            from ads_trading.trader.gateway.binance_gateway import BinanceGatewayConfig
            from ads_trading.trader.gateway.binance_gateway import BinanceGateway
            
            config = BinanceGatewayConfig(
                api_key=binance_api_key,
                api_secret=binance_api_secret,
                proxy_host='',
                proxy_port=0,
                testnet=False
            )

            # 创建币安网关
            gateway = BinanceGateway()
            
            # 连接到币安API
            connected = gateway.connect(config)
            if not connected:
                return {
                    "success": False,
                    "error": "币安网关连接失败"
                }

            # 获取账户余额
            account_info = {
                "spot": gateway.get_spot_balance(),
                "futures": gateway.get_futures_balance(),
                "total": gateway.get_total_balance()
            }
            return {
                'success': True,
                'account_info': account_info
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_binance_account(self):
        """获取币安账户数据"""
        try:
            # 从配置文件加载币安API密钥和密钥
            from ads_trading.trader.setting import SETTINGS
            
            binance_api_key = SETTINGS.get("binance.api_key", "")
            binance_api_secret = SETTINGS.get("binance.api_secret", "")
            
            if not binance_api_key or not binance_api_secret:
                return {
                    "success": False,
                    "error": "币安API密钥或密钥未配置"
                }
            
            # 创建币安网关配置
            from ads_trading.trader.gateway.binance_gateway import BinanceGatewayConfig
            from ads_trading.trader.gateway.binance_gateway import BinanceGateway
            
            config = BinanceGatewayConfig(
                api_key=binance_api_key,
                api_secret=binance_api_secret,
                proxy_host='',
                proxy_port=0,
                testnet=False
            )

            # 创建币安网关
            gateway = BinanceGateway()
            
            # 连接到币安API
            connected = gateway.connect(config)
            if not connected:
                return {
                    "success": False,
                    "error": "币安网关连接失败"
                }

            # 获取账户余额
            account_info = {
                "spot": gateway.get_spot_balance(),
                "futures": gateway.get_futures_balance(),
                "total": gateway.get_total_balance()
            }
            return {
                'success': True,
                'account_info': account_info
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_binance_account(self):
        """获取币安账户数据"""
        try:
            # 从配置文件加载币安API密钥和密钥
            from ads_trading.trader.setting import SETTINGS
            
            binance_api_key = SETTINGS.get("binance.api_key", "")
            binance_api_secret = SETTINGS.get("binance.api_secret", "")
            
            if not binance_api_key or not binance_api_secret:
                return {
                    "success": False,
                    "error": "币安API密钥或密钥未配置"
                }
            
            # 创建币安网关配置
            from ads_trading.trader.gateway.binance_gateway import BinanceGatewayConfig
            from ads_trading.trader.gateway.binance_gateway import BinanceGateway
            
            config = BinanceGatewayConfig(
                api_key=binance_api_key,
                api_secret=binance_api_secret,
                proxy_host='',
                proxy_port=0,
                testnet=False
            )

            # 创建币安网关
            gateway = BinanceGateway()
            
            # 连接到币安API
            connected = gateway.connect(config)
            if not connected:
                return {
                    "success": False,
                    "error": "币安网关连接失败"
                }

            # 获取账户余额
            account_info = {
                "spot": gateway.get_spot_balance(),
                "futures": gateway.get_futures_balance(),
                "total": gateway.get_total_balance()
            }
            return {
                'success': True,
                'account_info': account_info
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }


class WebServer:
    """Web 服务器"""

    def __init__(self):
        # 创建Flask应用并禁用默认静态文件路由
        self.app = Flask(__name__, static_folder=None)
        
        # 获取当前文件所在目录
        self.current_dir = os.path.dirname(__file__)
        self.templates_dir = os.path.join(self.current_dir, 'templates')
        self.static_dir = os.path.join(self.templates_dir, 'static')
        
        # 设置模板目录
        self.app.template_folder = self.templates_dir
        
        self.trading_engine = TradingEngine()
        self.setup_routes()

    def setup_routes(self):
        """设置路由"""
        # 1. 注册根路径路由
        self.app.add_url_rule('/', view_func=self.serve_index)
        
        # 2. 注册测试路由
        @self.app.route('/test')
        def test():
            return "Test route working", 200
        
        # 3. 注册API路由
        self.app.add_url_rule('/api/status', view_func=self.api_status, methods=['GET'])
        self.app.add_url_rule('/api/market', view_func=self.api_market_data, methods=['GET'])
        self.app.add_url_rule('/api/balance', view_func=self.api_balance, methods=['GET'])
        self.app.add_url_rule('/api/positions', view_func=self.api_positions, methods=['GET'])
        self.app.add_url_rule('/api/history', view_func=self.api_history, methods=['GET'])
        self.app.add_url_rule('/api/performance', view_func=self.api_performance, methods=['GET'])
        self.app.add_url_rule('/api/order', view_func=self.api_order, methods=['POST'])

        # 4. 注册静态文件路由 - 使用更具体的路径
        from flask import send_file
        @self.app.route('/static/js/<path:filename>')
        def serve_js(filename):
            """提供JS文件"""
            import os
            file_path = os.path.join(self.static_dir, 'js', filename)
            if os.path.exists(file_path):
                return send_file(file_path)
            else:
                return f"JS file not found: {file_path}", 404
        
        @self.app.route('/static/css/<path:filename>')
        def serve_css(filename):
            """提供CSS文件"""
            import os
            file_path = os.path.join(self.static_dir, 'css', filename)
            if os.path.exists(file_path):
                return send_file(file_path)
            else:
                return f"CSS file not found: {file_path}", 404
        
        @self.app.route('/static/media/<path:filename>')
        def serve_media(filename):
            """提供媒体文件"""
            import os
            file_path = os.path.join(self.static_dir, 'media', filename)
            if os.path.exists(file_path):
                return send_file(file_path)
            else:
                return f"Media file not found: {file_path}", 404
        
        # 5. 最后注册前端路由处理 - 只处理特定的前端路径模式
        @self.app.route('/dashboard')
        @self.app.route('/trading')
        @self.app.route('/settings')
        @self.app.route('/history')
        @self.app.route('/performance')
        def frontend_routes():
            """处理前端路由"""
            return self.serve_index()
        

    def serve_index(self):
        """提供首页"""
        return send_from_directory(self.build_dir, 'index.html')

    def serve_static(self, path):
        """提供静态文件 - 处理前端路由和其他静态资源"""
        file_path = os.path.join(self.build_dir, path)
        if os.path.isfile(file_path):
            return send_from_directory(self.build_dir, path)
        # 如果文件不存在，返回首页（支持前端路由）
        return send_from_directory(self.build_dir, 'index.html')

    def test(self):
        """测试路由"""
        return jsonify({'message': 'Test route works!'})

    def api_status(self):
        """API状态"""
        return jsonify({
            'status': 'running',
            'version': '1.0.0',
            'timestamp': time.time(),
            'server_time': time.strftime('%Y-%m-%d %H:%M:%S')
        })

    def api_market_data(self):
        """市场数据"""
        market_data = self.trading_engine.get_market_data()
        return jsonify(market_data)

    def api_balance(self):
        """账户余额"""
        balance = self.trading_engine.get_balance()
        return jsonify(balance)

    def api_positions(self):
        """持仓信息"""
        positions = self.trading_engine.get_positions()
        return jsonify(positions)

    def api_history(self):
        """交易历史"""
        history = self.trading_engine.get_trade_history()
        return jsonify(history)

    def api_performance(self):
        """性能指标"""
        performance = self.trading_engine.get_performance()
        return jsonify(performance)

    def api_order(self):
        """下单"""
        try:
            data = request.get_json()
            if not data:
                return jsonify({'error': 'No data provided'}), 400

            symbol = data.get('symbol')
            side = data.get('side')
            quantity = float(data.get('quantity', 0))

            if not all([symbol, side, quantity > 0]):
                return jsonify({'error': 'Invalid parameters'}), 400

            if side not in ['buy', 'sell']:
                return jsonify({'error': 'Invalid side'}), 400

            result = self.trading_engine.place_order(symbol, side, quantity)

            if 'error' in result:
                return jsonify(result), 400
            else:
                return jsonify(result)

        except Exception as e:
            return jsonify({'error': str(e)}), 500

    def run(self, host='0.0.0.0', port=5000, debug=False):
        """启动服务器"""
        # 设置静态文件缓存控制头
        @self.app.after_request
        def add_cache_control(response):
            if response.content_type.startswith('text/html'):
                response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
                response.headers['Pragma'] = 'no-cache'
                response.headers['Expires'] = '0'
            return response
        
        print(f"📍 Web UI available at: http://{host}:{port}")
        self.app.run(host=host, port=port, debug=debug, use_reloader=False)


class TradingEngine:
    """模拟交易引擎"""

    def __init__(self):
        self.balance = 10000.0
        self.positions = {}
        self.trade_history = []
        self.market_data = {
            'BTC/USDT': {'price': 45000.0, 'change': 2.5, 'volume': 28492},
            'ETH/USDT': {'price': 2500.0, 'change': -1.2, 'volume': 15932},
            'ADA/USDT': {'price': 0.45, 'change': 0.8, 'volume': 8921},
            'DOT/USDT': {'price': 6.5, 'change': 3.1, 'volume': 4532},
            'SOL/USDT': {'price': 120.5, 'change': 5.2, 'volume': 12345}
        }
        self.lock = Lock()
        self.running = True

        # 启动市场数据更新线程
        self.update_thread = Thread(target=self._update_market_data, daemon=True)
        self.update_thread.start()

    def _update_market_data(self):
        """模拟市场数据更新"""
        while self.running:
            time.sleep(3)  # 每3秒更新一次
            with self.lock:
                for symbol in self.market_data:
                    # 模拟价格波动
                    change = random.uniform(-2.0, 2.0)
                    current_price = self.market_data[symbol]['price']
                    new_price = max(0.01, current_price * (1 + change / 100))

                    # 更新数据
                    self.market_data[symbol]['price'] = round(new_price, 2)
                    self.market_data[symbol]['change'] = round(change, 2)
                    self.market_data[symbol]['volume'] = random.randint(1000, 30000)

    def get_market_data(self):
        """获取市场数据"""
        with self.lock:
            return self.market_data.copy()

    def get_balance(self):
        """获取账户余额"""
        total_balance = self.balance
        # 计算持仓价值
        for symbol, quantity in self.positions.items():
            if symbol in self.market_data:
                price = self.market_data[symbol]['price']
                total_balance += price * quantity

        return {
            'total': round(total_balance, 2),
            'available': round(self.balance, 2),
            'currency': 'USDT',
            'pnl': round(total_balance - 10000, 2)  # 初始资金10000
        }

    def place_order(self, symbol, side, quantity, order_type='market'):
        """下单"""
        with self.lock:
            if symbol not in self.market_data:
                return {'error': 'Invalid symbol'}

            price = self.market_data[symbol]['price']
            total_cost = price * quantity

            if side == 'buy' and total_cost > self.balance:
                return {'error': 'Insufficient balance'}

            if side == 'sell':
                if symbol not in self.positions or self.positions[symbol] < quantity:
                    return {'error': 'Insufficient position'}

            # 执行交易
            if side == 'buy':
                self.balance -= total_cost
                if symbol in self.positions:
                    self.positions[symbol] += quantity
                else:
                    self.positions[symbol] = quantity
            else:  # sell
                self.positions[symbol] -= quantity
                self.balance += total_cost
                if self.positions[symbol] == 0:
                    del self.positions[symbol]

            # 记录交易历史
            trade = {
                'id': len(self.trade_history) + 1,
                'symbol': symbol,
                'side': side,
                'quantity': quantity,
                'price': price,
                'total': round(total_cost, 2),
                'timestamp': time.time(),
                'datetime': time.strftime('%Y-%m-%d %H:%M:%S')
            }
            self.trade_history.append(trade)

            return {'success': True, 'trade': trade}

    def get_positions(self):
        """获取持仓"""
        positions_with_value = {}
        with self.lock:
            for symbol, quantity in self.positions.items():
                if symbol in self.market_data:
                    price = self.market_data[symbol]['price']
                    positions_with_value[symbol] = {
                        'quantity': quantity,
                        'current_price': price,
                        'value': round(price * quantity, 2)
                    }
        return positions_with_value

    def get_trade_history(self):
        """获取交易历史"""
        return self.trade_history[-20:]  # 返回最近20条记录

    def get_performance(self):
        """获取性能指标"""
        total_trades = len(self.trade_history)
        winning_trades = len([t for t in self.trade_history if t.get('profit', 0) > 0])

        return {
            'total_trades': total_trades,
            'winning_trades': winning_trades,
            'win_rate': round(winning_trades / total_trades * 100, 2) if total_trades > 0 else 0,
            'total_volume': round(sum(t['total'] for t in self.trade_history), 2)
        }
    
    def get_binance_account(self):
        """获取币安账户数据"""
        try:
            # 从配置文件加载币安API密钥和密钥
            from ads_trading.trader.setting import SETTINGS
            
            binance_api_key = SETTINGS.get("binance.api_key", "")
            binance_api_secret = SETTINGS.get("binance.api_secret", "")
            
            if not binance_api_key or not binance_api_secret:
                return {
                    "success": False,
                    "error": "币安API密钥或密钥未配置"
                }
            
            # 创建币安网关配置
            from ads_trading.trader.gateway.binance_gateway import BinanceGatewayConfig
            from ads_trading.trader.gateway.binance_gateway import BinanceGateway
            
            config = BinanceGatewayConfig(
                api_key=binance_api_key,
                api_secret=binance_api_secret,
                proxy_host='',
                proxy_port=0,
                testnet=False
            )

            # 创建币安网关
            gateway = BinanceGateway()
            
            # 连接到币安API
            connected = gateway.connect(config)
            if not connected:
                return {
                    "success": False,
                    "error": "币安网关连接失败"
                }

            # 获取账户余额
            account_info = {
                "spot": gateway.get_spot_balance(),
                "futures": gateway.get_futures_balance(),
                "total": gateway.get_total_balance()
            }
            return {
                'success': True,
                'account_info': account_info
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }


class WebServer:
    """Web 服务器"""

    def __init__(self):
        # Get the absolute path to the build directory
        self.build_dir = os.path.abspath('/Users/rocky/work/python/ADS-Trading/web-ui/build')
        static_dir = os.path.join(self.build_dir, 'static')
        
        print(f"Build directory: {self.build_dir}")
        print(f"Static directory: {static_dir}")
        print(f"Static folder exists: {os.path.exists(static_dir)}")
        
        # Initialize Flask app with working static folder configuration
        self.app = Flask(__name__, 
                        static_folder=static_dir,
                        static_url_path='/static')
                        
        self.trading_engine = TradingEngine()
        self.setup_routes()

    def setup_routes(self):
        """设置路由"""

        # 前端路由 - 返回index.html文件
        @self.app.route('/')
        def index():
            return send_from_directory(self.build_dir, 'index.html')

        # API 路由
        self.app.add_url_rule('/api/status', view_func=self.api_status, methods=['GET'])
        self.app.add_url_rule('/api/market', view_func=self.api_market_data, methods=['GET'])
        self.app.add_url_rule('/api/balance', view_func=self.api_balance, methods=['GET'])
        self.app.add_url_rule('/api/positions', view_func=self.api_positions, methods=['GET'])
        self.app.add_url_rule('/api/history', view_func=self.api_history, methods=['GET'])
        self.app.add_url_rule('/api/performance', view_func=self.api_performance, methods=['GET'])
        self.app.add_url_rule('/api/order', view_func=self.api_order, methods=['POST'])
        self.app.add_url_rule('/api/binance-account', view_func=self.api_binance_account, methods=['GET'])

        # Test route - temporarily commented out
        # self.app.add_url_rule('/test', view_func=self.test)

        # Serve index.html for root path
        self.app.add_url_rule('/', view_func=self.serve_index)

        # Handle frontend routes (React Router) - catch all other paths
        self.app.add_url_rule('/<path:path>', view_func=self.serve_static)

    def get_web_root(self):
        """获取 Web 根目录"""
        current_dir = os.path.dirname(__file__)
        return os.path.join(current_dir, 'templates')

    def serve_index(self):
        """提供首页"""
        web_root = self.get_web_root()
        return send_from_directory(web_root, 'index.html')

    def serve_static(self, path):
        """提供静态文件"""
        web_root = self.get_web_root()
        try:
            return send_from_directory(web_root, path)
        except:
            # 如果文件不存在，返回首页（支持前端路由）
            return send_from_directory(web_root, 'index.html')

    def api_status(self):
        """API状态"""
        return jsonify({
            'status': 'running',
            'version': '1.0.0',
            'timestamp': time.time(),
            'server_time': time.strftime('%Y-%m-%d %H:%M:%S')
        })

    def api_market_data(self):
        """市场数据"""
        market_data = self.trading_engine.get_market_data()
        return jsonify(market_data)

    def api_balance(self):
        """账户余额"""
        balance = self.trading_engine.get_balance()
        return jsonify(balance)

    def api_positions(self):
        """持仓信息"""
        positions = self.trading_engine.get_positions()
        return jsonify(positions)

    def api_history(self):
        """交易历史"""
        history = self.trading_engine.get_trade_history()
        return jsonify(history)

    def api_performance(self):
        """性能指标"""
        performance = self.trading_engine.get_performance()
        return jsonify(performance)

    def api_binance_account(self):
        """币安账户数据"""
        binance_account = self.trading_engine.get_binance_account()
        return jsonify(binance_account)

    def api_order(self):
        """下单"""
        try:
            data = request.get_json()
            if not data:
                return jsonify({'error': 'No data provided'}), 400

            symbol = data.get('symbol')
            side = data.get('side')
            quantity = float(data.get('quantity', 0))

            if not all([symbol, side, quantity > 0]):
                return jsonify({'error': 'Invalid parameters'}), 400

            if side not in ['buy', 'sell']:
                return jsonify({'error': 'Invalid side'}), 400

            result = self.trading_engine.place_order(symbol, side, quantity)

            if 'error' in result:
                return jsonify(result), 400
            else:
                return jsonify(result)

        except Exception as e:
            return jsonify({'error': str(e)}), 500

    def run(self, host='0.0.0.0', port=5000, debug=False):
        """启动服务器"""
        print(f"📍 Web UI available at: http://{host}:{port}")
        self.app.run(host=host, port=port, debug=debug, use_reloader=False)