"""
Gunicorn configuration file for running simple test server
"""
bind = "0.0.0.0:8888"
workers = 2
accesslog = "-"
errorlog = "-"
reload = True