# internal-bot

This repository is home to the internal bot we use on the EPS server.

## Overview

The bot's main goal is to make life easier for the conference teams by streamlining workflows and integrating with other services.


## Design Decisions

* **One Codebase, Multiple Entry Points**
  * **HTTP Endpoint**: Handles webhooks.
  * **Discord Bot**: Lets us communicate back and forth with Discord.
    * It can post scheduled messages and respond to messages, commands, and events on the server.
  * **Background Worker**: Mainly processes HTTP requests but can also be used within the bot itself.

* **Small-Scale Setup**
  * Built to be easily extendable with new features, but designed for low-traffic environments like the EPS Organizers server.

## Tech Stack and Implementation Choices

* **Django**
  * Handles the HTTP layer, database, and general framework duties.
  * Why Django?
    * It's popular and easy to work with.
    * Comes with great built-in tools like ORM, migrations, and Django admin for quick access to data.
    * We're already using it for other EPS projects.

* **PostgreSQL**
  * Both development and production setups can run using Docker Compose.

* **discord.py**
  * Handles the Discord integration.
  * Runs in the same environment as Django, so we can reuse code, models, and the database.
  * The bot runs as a Django management command.

* **django-tasks**
  * Keeps background task management simple by storing tasks in the database—no need for extra tools like Redis or RabbitMQ.

* **Deployment**
  * Deployed on a dedicated VPS just for the bot.
  * Packaged as a single Docker image with multiple entry points.
  * Deployed using Ansible to match the deployment setup we use for other EPS projects.
    * We use separate playbooks for setting up a VPS and deploying the app.
  * Uses Docker Compose for simplicity.
  * Separate playbooks for Nginx (for the HTTP endpoint) and the app.

* **Dependency Management**
  * Managed with `uv`. All Makefiles, Docker images, and related configs are set up to use `uv`.

* **CI/CD**
  * Built with GitHub Actions
  * Runs tests and linters on every push to pull requests
  * Automatically deploys to production when code is merged to `main`

## Documentation

Check the `docs/` directory for additional information:

* [Architecture Overview](docs/architecture.md) - Basic system design and integration workflow
* [Deployment Guide](docs/deployment.md) - Server setup and deployment process

## Local Development


### FAQ
####  Using M1 Mac, and psycopg doesn't work?

Make sure that your Python installation is compiled with lipbq correctly.
In case of using brew and pyenv this could help:

```
$ brew link --force libpq
$ export PATH="/opt/homebrew/opt/libpq/bin:$PATH"
$ pyenv install 3.12
```

...

## Contributing

### Setting Up Development Environment

1. Clone the repository
2. Install `uv` - all the dependencies and Makefile targets are using `uv`.
3. Set up environment variables in `.env` file
4. Run the database with `docker-compose up -d`
5. Apply migrations with `make migrate`
6. Run the development server with `make server`
7. Run the bot with `make bot`
8. Run the worker with `make worker`

You can check the Django admin at http://localhost:4672/admin/ to see webhooks and tasks.

### Adding a New Integration

1. Create a module in `intbot/core/integrations/`
2. Define Pydantic models to organize the data
3. Add a webhook endpoint in `core/endpoints/webhooks.py`
4. Add security checks (signature verification)
5. Update `process_webhook` in `core/tasks.py`
6. If it will send Discord messages, add routing logic in `channel_router.py`
7. Add the new URL in `urls.py`

### Testing

The project uses pytest with Django:
- Run all tests with `make test`
- Run single tests with `make test/k K=your_keyword`
- Run fast tests with `make test/fast`
- Check test coverage with `make test/cov`

When testing webhooks, make sure to test:
- Security checks (signature verification)
- Data parsing
- Channel routing (if using Discord)
- Message formatting (if using Discord)

### Code Quality

We use ruff and mypy to lint and format the project.
Both of those are run on CI for every Pull Request.

- Use type hints for all functions and classes
- Run `make format` before committing
- Run `make lint` and `make type-check` to check for issues
- Follow the same error handling patterns as existing code

## Operations

TODO: Expand on this part :)

### Monitoring

- Currently not configured

### Debugging

- Logs can be viewed on the intbot_user with `make logs`
- The Django admin interface is available at `/admin/`

## Deployment

Currently deployed to a separate VPS, using ansible (for both provisioning and deployment).

See deployment doc for more details: [Deployment Guide](docs/deployment.md)
