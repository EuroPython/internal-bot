DEV_CMD=cd intbot && DJANGO_ENV="dev" uv run ./manage.py
TEST_CMD=cd intbot && DJANGO_SETTINGS_MODULE="intbot.settings" DJANGO_ENV="test" uv run pytest --nomigrations


help:
	# First target is dummy so we you won't run anything by accident
	@echo "Hello world!, Please check the file content for details"

server:
	$(DEV_CMD) runserver 0.0.0.0:4672

shell:
	$(DEV_CMD) shell_plus

migrate:
	$(DEV_CMD) migrate

migrations:
	$(DEV_CMD) makemigrations -n $(N)

test:
	$(TEST_CMD) -s -vv
