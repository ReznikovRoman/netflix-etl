command = '/usr/bin/gunicorn'
bind = "0.0.0.0:8000"
workers = 3
timeout = 300
limit_request_fields = 32000
limit_request_field_size = 0
