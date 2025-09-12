# Welcome! :)

# Test/Dev
DEV_CMD=cd intbot && DJANGO_ENV="dev" uv run --env-file .env -- ./manage.py
TEST_CMD=DJANGO_SETTINGS_MODULE="intbot.settings" DJANGO_ENV="test" uv run pytest --nomigrations
UV_RUN_DEV=cd intbot && DJANGO_ENV="dev" uv run

# Docker
DOCKER_RUN_WITH_PORT=docker run -p 4672:4672 --add-host=host.internal:host-gateway -e DJANGO_ENV="local_container" -it intbot:$(V)
DOCKER_RUN=docker run --add-host=host.internal:host-gateway -e DJANGO_ENV="test" -it intbot:$(V)
MANAGE=cd intbot && ./manage.py
# In container we run with migrations
CONTAINER_TEST_CMD=DJANGO_SETTINGS_MODULE="intbot.settings" DJANGO_ENV="test" pytest --migrations
CI_RUN=cd intbot && DJANGO_SETTINGS_MODULE="intbot.settings" DJANGO_ENV="ci"

# Deployment
DEPLOY_CMD=cd deploy && uvx --from "ansible-core" ansible-playbook -i hosts.yml
DEPLOY_LINT_CMD=cd deploy && uvx --from "ansible-lint" ansible-lint

# mostly useful for docker and deployment
current_git_hash=$(shell git rev-parse HEAD)
V ?= $(current_git_hash)


help:
	# First target is dummy so we you won't run anything by accident
	@echo "Hello world!, Please check the file content for details"



# Local development
# =================

db:
	docker compose up -d

server:
	$(DEV_CMD) runserver 0.0.0.0:4672

shell:
	$(DEV_CMD) shell_plus

migrate:
	$(DEV_CMD) migrate

migrations:
	$(DEV_CMD) makemigrations -n $(N)

manage:
	$(DEV_CMD) $(ARG)

bot:
	$(DEV_CMD) run_bot

worker:
	$(DEV_CMD) db_worker -v 2


# Test, lint, etc
# ================

test:
	$(TEST_CMD) -s -v

test_last_failed:
	$(TEST_CMD) -s -vv --last-failed

test_: test_last_failed

test/k:
	$(TEST_CMD) -s -v -k $(K)

test/fast:
	# skip slow tests
	$(TEST_CMD) -s -v -m "not slow"

test/cov:
	$(TEST_CMD) --cov=. --cov-report=term


lint:
	# '.' because UV_RUN_DEV implies cd to intbot/
	$(UV_RUN_DEV) ruff check .

lint/fix:
	# '.' because UV_RUN_DEV implies cd to intbot/
	$(UV_RUN_DEV) ruff check --fix .

format:
	# '.' because UV_RUN_DEV implies cd to intbot/
	$(UV_RUN_DEV) ruff format .

type-check:
	$(UV_RUN_DEV) mypy intbot/



client/send_test_webhook:
	uv run client/send_test_webhook.py


# Targets to be run inside the container (for build/prod/deployments)
# ===================================================================

in-container/collectstatic:
	DJANGO_ENV="build" python intbot/manage.py collectstatic --noinput

in-container/gunicorn:
	# DJANGO_ENV should be passed to docker
	cd intbot && gunicorn

in-container/bot:
	$(MANAGE) run_bot

in-container/worker:
	$(MANAGE) db_worker -v 2

in-container/migrate:
	$(MANAGE) migrate

in-container/manage:
	$(MANAGE) $(ARG)

in-container/tests:
	$(CONTAINER_TEST_CMD) -vvv

ci/lint:
	$(CI_RUN) ruff check .

ci/type-check:
	$(CI_RUN) mypy intbot


# Docker management targets
# =========================

docker/build:
	docker build . -t intbot:$(current_git_hash) -t intbot:latest

docker/run/gunicorn:
	$(DOCKER_RUN_WITH_PORT) make in-container/gunicorn

docker/run/tests:
	$(DOCKER_RUN) make in-container/tests

docker/run/lint:
	$(DOCKER_RUN) make ci/lint
	$(DOCKER_RUN) make ci/type-check


# Deploymenet targets
# ====================

deploy/provision:
	$(DEPLOY_CMD) playbooks/01_setup.yml
	$(DEPLOY_CMD) playbooks/02_nginx.yml

deploy/app:
	@echo "Deploying version $(V) to a remote server"
	$(DEPLOY_CMD) playbooks/03_app.yml --extra-vars "app_version=$(V)"
	$(DEPLOY_CMD) playbooks/04_cron.yml

lint/deploy:
	$(DEPLOY_LINT_CMD) playbooks/01_setup.yml
	$(DEPLOY_LINT_CMD) playbooks/02_nginx.yml
	$(DEPLOY_LINT_CMD) playbooks/03_app.yml
