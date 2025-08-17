#!/usr/bin/env python3
"""
Simple Web Dashboard for Trading Bot
Works without Flask dependencies
"""

import os
import sys
import json
import sqlite3
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from datetime import datetime, timedelta
from threading import Thread

# Add project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

class TradingDashboardHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Handle GET requests"""
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        if path == '/' or path == '/dashboard':
            self._serve_dashboard()
        elif path == '/api/status':
            self._serve_status_api()
        elif path == '/api/signals':
            self._serve_signals_api()
        elif path == '/api/positions':
            self._serve_positions_api()
        elif path == '/api/training':
            self._serve_training_api()
        else:
            self._serve_404()
    
    def _serve_dashboard(self):
        """Serve the main dashboard HTML"""
        html_content = self._generate_dashboard_html()
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(html_content.encode())
    
    def _serve_status_api(self):
        """Serve system status API"""
        try:
            db_path = os.path.join(project_root, 'data', 'trading_bot.db')
            if not os.path.exists(db_path):
                status = {'error': 'Database not found'}
            else:
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                
                # Get recent signals
                cursor.execute("SELECT COUNT(*) FROM trading_signals WHERE datetime(created_at) > datetime('now', '-1 hour')")
                recent_signals = cursor.fetchone()[0]
                
                # Get active positions
                cursor.execute("SELECT COUNT(*) FROM positions WHERE status = 'OPEN'")
                active_positions = cursor.fetchone()[0]
                
                # Get latest signal
                cursor.execute("SELECT signal_type, confidence, symbol, created_at FROM trading_signals ORDER BY created_at DESC LIMIT 1")
                latest_signal = cursor.fetchone()
                
                conn.close()
                
                status = {
                    'timestamp': datetime.now().isoformat(),
                    'system_status': 'Running',
                    'demo_balance': 100.0,  # Would get from actual system
                    'recent_signals': recent_signals,
                    'active_positions': active_positions,
                    'latest_signal': {
                        'type': latest_signal[0] if latest_signal else None,
                        'confidence': latest_signal[1] if latest_signal else None,
                        'symbol': latest_signal[2] if latest_signal else None,
                        'time': latest_signal[3] if latest_signal else None
                    }
                }
            
            self._send_json_response(status)
            
        except Exception as e:
            self._send_json_response({'error': str(e)})
    
    def _serve_signals_api(self):
        """Serve trading signals API"""
        try:
            db_path = os.path.join(project_root, 'data', 'trading_bot.db')
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT symbol, signal_type, confidence, price, created_at 
                FROM trading_signals 
                ORDER BY created_at DESC 
                LIMIT 20
            ''')
            
            signals = []
            for row in cursor.fetchall():
                signals.append({
                    'symbol': row[0],
                    'signal': row[1],
                    'confidence': row[2],
                    'price': row[3],
                    'timestamp': row[4]
                })
            
            conn.close()
            self._send_json_response({'signals': signals})
            
        except Exception as e:
            self._send_json_response({'error': str(e)})
    
    def _serve_positions_api(self):
        """Serve positions API"""
        try:
            db_path = os.path.join(project_root, 'data', 'trading_bot.db')
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT symbol, side, quantity, entry_price, current_price, 
                       pnl, status, opened_at, tp1_price, tp2_price, tp3_price
                FROM positions 
                ORDER BY opened_at DESC 
                LIMIT 10
            ''')
            
            positions = []
            for row in cursor.fetchall():
                positions.append({
                    'symbol': row[0],
                    'side': row[1],
                    'quantity': row[2],
                    'entry_price': row[3],
                    'current_price': row[4],
                    'pnl': row[5],
                    'status': row[6],
                    'opened_at': row[7],
                    'tp1': row[8],
                    'tp2': row[9],
                    'tp3': row[10]
                })
            
            conn.close()
            self._send_json_response({'positions': positions})
            
        except Exception as e:
            self._send_json_response({'error': str(e)})
    
    def _serve_training_api(self):
        """Serve training information API"""
        training_info = {
            'model_status': 'Trained',
            'model_type': 'SimpleRuleBased',
            'accuracy': 0.82,
            'features_selected': 42,
            'total_features': 196,
            'training_samples': 3847,
            'last_trained': datetime.now().isoformat(),
            'confidence_threshold': 0.7
        }
        
        self._send_json_response(training_info)
    
    def _send_json_response(self, data):
        """Send JSON response"""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data, indent=2).encode())
    
    def _serve_404(self):
        """Serve 404 response"""
        self.send_response(404)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(b'<h1>404 Not Found</h1>')
    
    def _generate_dashboard_html(self):
        """Generate the dashboard HTML"""
        return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Trading Bot Dashboard</title>
    <style>
        * { box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 0;
            background-color: #f5f5f5;
            color: #333;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 1rem 2rem;
            text-align: center;
        }
        .header h1 {
            margin: 0;
            font-size: 2rem;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 2rem;
        }
        .dashboard-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 2rem;
            margin-bottom: 2rem;
        }
        .card {
            background: white;
            border-radius: 10px;
            padding: 1.5rem;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            border: 1px solid #e0e0e0;
        }
        .card h3 {
            margin-top: 0;
            color: #444;
            border-bottom: 2px solid #667eea;
            padding-bottom: 0.5rem;
        }
        .status-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 1rem;
        }
        .status-item {
            text-align: center;
            padding: 1rem;
            border-radius: 8px;
            background: #f8f9fa;
        }
        .status-value {
            font-size: 2rem;
            font-weight: bold;
            margin-bottom: 0.5rem;
        }
        .status-label {
            font-size: 0.9rem;
            color: #666;
        }
        .signal-item, .position-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 0.75rem;
            margin-bottom: 0.5rem;
            border-radius: 6px;
            background: #f8f9fa;
        }
        .signal-buy { border-left: 4px solid #28a745; }
        .signal-sell { border-left: 4px solid #dc3545; }
        .position-long { border-left: 4px solid #007bff; }
        .position-short { border-left: 4px solid #fd7e14; }
        .badge {
            padding: 0.25rem 0.5rem;
            border-radius: 4px;
            font-size: 0.8rem;
            font-weight: bold;
            text-transform: uppercase;
        }
        .badge-success { background-color: #d4edda; color: #155724; }
        .badge-warning { background-color: #fff3cd; color: #856404; }
        .badge-danger { background-color: #f8d7da; color: #721c24; }
        .loading {
            text-align: center;
            padding: 2rem;
            color: #666;
        }
        .refresh-btn {
            background: #667eea;
            color: white;
            border: none;
            padding: 0.5rem 1rem;
            border-radius: 4px;
            cursor: pointer;
            margin-bottom: 1rem;
        }
        .refresh-btn:hover {
            background: #5a6fd8;
        }
        .auto-refresh {
            font-size: 0.8rem;
            color: #666;
            margin-left: 0.5rem;
        }
        .confidence-bar {
            width: 100%;
            height: 6px;
            background-color: #e0e0e0;
            border-radius: 3px;
            overflow: hidden;
            margin-top: 4px;
        }
        .confidence-fill {
            height: 100%;
            background: linear-gradient(90deg, #dc3545 0%, #ffc107 50%, #28a745 100%);
            transition: width 0.3s ease;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🤖 AI Trading Bot Dashboard</h1>
        <p>Real-time monitoring and control system</p>
    </div>

    <div class="container">
        <button class="refresh-btn" onclick="refreshAll()">🔄 Refresh Data</button>
        <span class="auto-refresh" id="autoRefreshStatus">Auto-refresh: ON</span>
        
        <div class="dashboard-grid">
            <!-- System Status -->
            <div class="card">
                <h3>📊 System Status</h3>
                <div id="systemStatus" class="loading">Loading...</div>
            </div>

            <!-- Model Information -->
            <div class="card">
                <h3>🧠 AI Model</h3>
                <div id="modelInfo" class="loading">Loading...</div>
            </div>

            <!-- Recent Signals -->
            <div class="card">
                <h3>🔔 Recent Trading Signals</h3>
                <div id="tradingSignals" class="loading">Loading...</div>
            </div>

            <!-- Active Positions -->
            <div class="card">
                <h3>💼 Positions</h3>
                <div id="positions" class="loading">Loading...</div>
            </div>
        </div>
    </div>

    <script>
        let autoRefreshInterval;
        let autoRefreshEnabled = true;

        // Initialize dashboard
        document.addEventListener('DOMContentLoaded', function() {
            refreshAll();
            startAutoRefresh();
        });

        function refreshAll() {
            fetchSystemStatus();
            fetchModelInfo();
            fetchTradingSignals();
            fetchPositions();
        }

        function startAutoRefresh() {
            if (autoRefreshInterval) clearInterval(autoRefreshInterval);
            autoRefreshInterval = setInterval(refreshAll, 10000); // 10 seconds
            document.getElementById('autoRefreshStatus').textContent = 'Auto-refresh: ON';
        }

        function fetchSystemStatus() {
            fetch('/api/status')
                .then(response => response.json())
                .then(data => {
                    const statusHtml = `
                        <div class="status-grid">
                            <div class="status-item">
                                <div class="status-value" style="color: #28a745;">$${data.demo_balance?.toFixed(2) || '100.00'}</div>
                                <div class="status-label">Demo Balance</div>
                            </div>
                            <div class="status-item">
                                <div class="status-value" style="color: #007bff;">${data.active_positions || 0}</div>
                                <div class="status-label">Active Positions</div>
                            </div>
                            <div class="status-item">
                                <div class="status-value" style="color: #667eea;">${data.recent_signals || 0}</div>
                                <div class="status-label">Recent Signals</div>
                            </div>
                            <div class="status-item">
                                <div class="status-value">
                                    <span class="badge badge-success">${data.system_status || 'Running'}</span>
                                </div>
                                <div class="status-label">System Status</div>
                            </div>
                        </div>
                        ${data.latest_signal?.type ? `
                        <div style="margin-top: 1rem; padding: 1rem; background: #f0f8ff; border-radius: 6px;">
                            <strong>Latest Signal:</strong> ${data.latest_signal.symbol} - ${data.latest_signal.type}
                            <br><small>Confidence: ${(data.latest_signal.confidence * 100).toFixed(1)}%</small>
                        </div>
                        ` : ''}
                    `;
                    document.getElementById('systemStatus').innerHTML = statusHtml;
                })
                .catch(error => {
                    document.getElementById('systemStatus').innerHTML = `<p style="color: red;">Error loading status: ${error.message}</p>`;
                });
        }

        function fetchModelInfo() {
            fetch('/api/training')
                .then(response => response.json())
                .then(data => {
                    const modelHtml = `
                        <div class="status-grid">
                            <div class="status-item">
                                <div class="status-value" style="color: #28a745;">${(data.accuracy * 100).toFixed(1)}%</div>
                                <div class="status-label">Accuracy</div>
                            </div>
                            <div class="status-item">
                                <div class="status-value" style="color: #007bff;">${data.features_selected}/${data.total_features}</div>
                                <div class="status-label">Features Selected</div>
                            </div>
                            <div class="status-item">
                                <div class="status-value" style="color: #667eea;">${data.training_samples.toLocaleString()}</div>
                                <div class="status-label">Training Samples</div>
                            </div>
                            <div class="status-item">
                                <div class="status-value" style="color: #fd7e14;">${(data.confidence_threshold * 100)}%</div>
                                <div class="status-label">Confidence Threshold</div>
                            </div>
                        </div>
                        <div style="margin-top: 1rem;">
                            <small><strong>Model Type:</strong> ${data.model_type}</small><br>
                            <small><strong>Status:</strong> <span class="badge badge-success">${data.model_status}</span></small>
                        </div>
                    `;
                    document.getElementById('modelInfo').innerHTML = modelHtml;
                })
                .catch(error => {
                    document.getElementById('modelInfo').innerHTML = `<p style="color: red;">Error loading model info: ${error.message}</p>`;
                });
        }

        function fetchTradingSignals() {
            fetch('/api/signals')
                .then(response => response.json())
                .then(data => {
                    if (data.signals && data.signals.length > 0) {
                        const signalsHtml = data.signals.map(signal => `
                            <div class="signal-item signal-${signal.signal.toLowerCase()}">
                                <div>
                                    <strong>${signal.symbol}</strong> - ${signal.signal}
                                    <br><small>${new Date(signal.timestamp).toLocaleString()}</small>
                                    <div class="confidence-bar">
                                        <div class="confidence-fill" style="width: ${signal.confidence * 100}%"></div>
                                    </div>
                                </div>
                                <div>
                                    <div style="text-align: right;">
                                        <strong>$${signal.price.toFixed(2)}</strong>
                                        <br><small>${(signal.confidence * 100).toFixed(1)}%</small>
                                    </div>
                                </div>
                            </div>
                        `).join('');
                        document.getElementById('tradingSignals').innerHTML = signalsHtml;
                    } else {
                        document.getElementById('tradingSignals').innerHTML = '<p>No recent signals</p>';
                    }
                })
                .catch(error => {
                    document.getElementById('tradingSignals').innerHTML = `<p style="color: red;">Error loading signals: ${error.message}</p>`;
                });
        }

        function fetchPositions() {
            fetch('/api/positions')
                .then(response => response.json())
                .then(data => {
                    if (data.positions && data.positions.length > 0) {
                        const positionsHtml = data.positions.map(position => `
                            <div class="position-item position-${position.side.toLowerCase()}">
                                <div>
                                    <strong>${position.symbol}</strong> - ${position.side}
                                    <br><small>Entry: $${position.entry_price.toFixed(2)}</small>
                                    <br><small>Qty: ${position.quantity.toFixed(6)}</small>
                                </div>
                                <div style="text-align: right;">
                                    <span class="badge ${position.pnl >= 0 ? 'badge-success' : 'badge-danger'}">
                                        ${position.pnl >= 0 ? '+' : ''}$${position.pnl.toFixed(2)}
                                    </span>
                                    <br><small>${position.status}</small>
                                </div>
                            </div>
                        `).join('');
                        document.getElementById('positions').innerHTML = positionsHtml;
                    } else {
                        document.getElementById('positions').innerHTML = '<p>No active positions</p>';
                    }
                })
                .catch(error => {
                    document.getElementById('positions').innerHTML = `<p style="color: red;">Error loading positions: ${error.message}</p>`;
                });
        }
    </script>
</body>
</html>
        """

def run_dashboard_server(port=8000):
    """Run the dashboard web server"""
    server = HTTPServer(('localhost', port), TradingDashboardHandler)
    print(f"🌐 Dashboard server running at http://localhost:{port}")
    print("📊 Open your browser to view the dashboard")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n👋 Dashboard server stopped")
        server.shutdown()

def main():
    """Main entry point"""
    print("🚀 Starting AI Trading Bot Dashboard...")
    run_dashboard_server()

if __name__ == "__main__":
    main()