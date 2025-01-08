

help:
	# First target is dummy so we you won't run anything by accident
	@echo "Hello world!, Please check the file content for details"

server:
	cd intbot && DJANGO_ENV="dev" uv run ./manage.py runserver 0.0.0.0:4672

migrate:
	cd intbot && DJANGO_ENV="dev" uv run ./manage.py migrate

test:
	cd intbot && DJANGO_SETTINGS_MODULE="intbot.settings" DJANGO_ENV="test" uv run pytest
