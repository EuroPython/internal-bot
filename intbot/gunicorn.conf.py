bind = "0.0.0.0:4672"

# We want to run it in a small conatiner
workers = 2 + 1

wsgi_app = "intbot.wsgi:application"

# logging
loglevel = "info"
accesslog = "-"
errorlog = "-"

# env
raw_env = ["DJANGO_SETTINGS_MODULE=intbot.settings"]
