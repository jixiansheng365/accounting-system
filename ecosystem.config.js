module.exports = {
  apps: [{
    name: 'accounting-system',
    script: 'venv/bin/gunicorn',
    args: '-w 2 -b 127.0.0.1:5000 "app:create_app(\'production\')"',
    cwd: '/www/wwwroot/accounting-system',
    interpreter: 'none',
    env: {
      'FLASK_ENV': 'production',
      'SECRET_KEY': 'your-secret-key-change-this-in-production',
      'DATABASE_URL': 'sqlite:///data/accounting.db'
    },
    error_file: 'logs/pm2-error.log',
    out_file: 'logs/pm2-out.log',
    log_date_format: 'YYYY-MM-DD HH:mm:ss Z',
    instances: 1,
    autorestart: true,
    watch: false,
    max_memory_restart: '1G'
  }]
}
