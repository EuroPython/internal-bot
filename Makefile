# Welcome! :)

# Test/Dev
DEV_CMD=cd intbot && DJANGO_ENV="dev" uv run --env-file .env -- ./manage.py
TEST_CMD=cd intbot && DJANGO_SETTINGS_MODULE="intbot.settings" DJANGO_ENV="test" uv run pytest --nomigrations

# Docker
DOCKER_RUN_WITH_PORT=docker run -p 4672:4672 --add-host=host.internal:host-gateway -e DJANGO_ENV="local_container" -it intbot:$(V)
MANAGE=cd intbot && ./manage.py

# Deployment
DEPLOY_CMD=cd deploy && uvx --from "ansible-core" ansible-playbook -i hosts.yml

# mostly useful for docker and deployment
current_git_hash=$(shell git rev-parse HEAD)
V ?= $(current_git_hash)


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

bot:
	$(DEV_CMD) run_bot


client/send_test_webhook:
	uv run client/send_test_webhook.py


# Targets to be run inside the container (for build/prod/deployments)

in-container/collectstatic:
	DJANGO_ENV="build" python intbot/manage.py collectstatic --noinput

in-container/gunicorn:
	# DJANGO_ENV should be passed to docker
	cd intbot && gunicorn

in-container/bot:
	$(MANAGE) run_bot

in-container/migrate:
	$(MANAGE) migrate


# Docker management targets

docker/build:
	docker build . -t intbot:$(current_git_hash)

docker/run/gunicorn:
	$(DOCKER_RUN_WITH_PORT) make in-container/gunicorn


# Deploymenet targets
#
deploy/provision:
	$(DEPLOY_CMD) playbooks/01_setup.yml
	$(DEPLOY_CMD) playbooks/02_nginx.yml

deploy/app:
	@echo "Deploying version $(V) to a remote server"
	$(DEPLOY_CMD) playbooks/03_app.yml --extra-vars "app_version=$(V)"
