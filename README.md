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
  * Built with GitHub Actions.

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

...

## Operations

...

## Deployment

...

