# Deployment Guide

This document explains how to deploy the internal-bot to a production environment.

## Overview

The deployment process uses:
- Docker for containerization
- Docker Compose for container orchestration
- Ansible for automation
- Nginx for web server and SSL termination

The application is deployed as several containers:
- Django web app (handles webhooks)
- Discord bot (sends messages to Discord)
- Background worker (processes tasks)
- PostgreSQL database

## Prerequisites

- A server running Ubuntu
- SSH access to the server
- Domain name pointing to the server
- uv installed on your local machine (it will automatically download and install ansible, if you run it from the `make deploy/*` targets.

## Deployment Process

The deployment is done in three stages using Ansible playbooks:

### 1. Server Setup

```bash
make deploy/provision
```

This runs the first two playbooks:
- `01_setup.yml`: Sets up server, installs Docker, creates users (nginx_user and intbot_user)
- `02_nginx.yml`: Configures Nginx with SSL certificates

### 2. Application Deployment

```bash
make deploy/app
```

This runs the `03_app.yml` playbook which:
- Builds Docker images
- Sets up environment variables
- Creates Docker Compose configuration
- Runs database migrations
- Starts all services

## Ansible Templates and Separate User Environments

The deployment uses a separated approach with different users for different responsibilities:

### Separate Users and Docker Compose Files

1. **Nginx Environment** (managed by `nginx_user`):
   - Uses its own Docker Compose file generated from `docker-compose.nginx.yml.j2`
   - Handles SSL termination and proxying
   - Has access to port 80/443 for web traffic

2. **Application Environment** (managed by `intbot_user`):
   - Uses its own Docker Compose file generated from `docker-compose.app.yml.j2`
   - Runs Django app, Discord bot, worker, and database
   - Doesn't need direct public internet access

Both environments are connected via a shared Docker network called "shared_with_nginx_network". This architecture provides several benefits:
- **Security**: Each component runs with minimal required permissions
- **Access Control**: Different teams can have access to different parts (some only to app, some to both)
- **Separation of Concerns**: Nginx configuration changes don't affect the application
- **Maintenance**: Either component can be updated independently

### Custom Makefiles for Each Environment

Ansible generates two specialized Makefiles:

1. **Nginx Makefile** (`Makefile.nginx.j2`):
   - Focused on SSL certificate management
   - Key targets:
     - `certbot/init-staging`: Set up staging certificates (for testing)
     - `certbot/upgrade-to-prod`: Upgrade to production certificates
     - `certbot/renew`: Renew existing certificates
     - `certbot/force-reissue-PROD-certificate`: Force reissue production certificates

2. **Application Makefile** (`Makefile.app.j2`):
   - Focused on application management
   - All commands use the `prod/` prefix
   - Key targets:
     - `prod/migrate`: Run database migrations
     - `prod/shell`: Access Django shell
     - `prod/db_shell`: Access database shell
     - `prod/manage`: Run Django management commands
     - `logs`: View application logs

## Version Control

Deployments are tied to specific Git commits:

```bash
# Deploy specific version
make deploy/app V=abcd1234
```

If no version is specified, the current Git commit hash is used.

## Environment Variables

The application needs these environment variables in `intbot.env`:

- `DJANGO_SECRET_KEY`: Secret key for Django
- `DJANGO_ALLOWED_HOSTS`: Comma-separated list of allowed hosts
- `DATABASE_URL`: PostgreSQL connection string
- `DISCORD_BOT_TOKEN`: Discord bot authentication token
- `DISCORD_GUILD_ID`: Discord server ID
- `GITHUB_WEBHOOK_SECRET`: Secret for GitHub webhook verification
- `GITHUB_TOKEN`: GitHub API token
- `ZAMMAD_WEBHOOK_SECRET`: Secret for Zammad webhook verification

An example file is available at `deploy/templates/app/intbot.env.example`.

## Monitoring

- Logs can be viewed with `docker compose logs`
- The Django admin interface is available at `/admin/`
- Server monitoring should be set up separately (not included)

## Troubleshooting

Common issues:
- **Webhook verification failures**: Check secret keys in environment variables
- **Database connection errors**: Verify DATABASE_URL is correct
- **Discord messages not being sent**: Check DISCORD_BOT_TOKEN and permissions

For more detailed logs:
```bash
docker compose logs -f bot
docker compose logs -f web
docker compose logs -f worker
```

Or even simpler if you want to see all of them at once
```bash
make logs
```
