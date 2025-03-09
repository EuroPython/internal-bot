# Internal Bot Architecture

## Overview

The internal-bot helps EuroPython Society teams communicate better. Right now it connects GitHub and Zammad with Discord, but it's built to do more in the future.

The app has three main parts:
1. **Django Web App**: Receives webhooks, provides an admin panel, and will support more features later
2. **Discord Bot**: Sends messages to Discord and responds to commands
3. **Background Worker**: Handles tasks in the background without blocking the web app

## System Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌────────────────┐
│  External       │     │                  │     │                │
│  Services       │────▶│  Django App      │────▶│  Discord       │
│  (GitHub,       │     │  (Webhook API)   │     │  Channels      │
│  Zammad)        │     │                  │     │                │
└─────────────────┘     └──────────────────┘     └────────────────┘
                               │   ▲
                               ▼   │
                        ┌──────────────────┐
                        │                  │
                        │  Database        │
                        │  (PostgreSQL)    │
                        │                  │
                        └──────────────────┘
```

### Data Flow

1. External services send webhooks to our app
2. We verify and save these webhooks to the database
3. Our background worker processes these webhooks:
   - For some webhooks (like GitHub), we need to fetch more data to make them useful
   - We then turn the webhook data into a format we can use
4. If a Discord message needs to be sent, the channel router picks the right channel
5. Discord messages are saved to the database
6. The Discord bot checks for new messages and sends them

### Using the Admin Panel

The Django Admin panel lets you:
- See all webhooks and filter them by type or date
- Look at the raw webhook data
- Check if tasks worked or failed
- Manually trigger processing for webhooks
- View and manage Discord messages

## Key Components

### Models

- **Webhook**: Stores webhook data including source, event type, and content
- **DiscordMessage**: Represents a message to be sent to Discord
- **Task**: (django-tasks) Stores background task execution history

### Integrations

#### GitHub Integration
- Receives webhooks at `/webhooks/github/`
- Verifies signatures using HMAC-SHA256
- Currently handles project item events and issues
- Routes messages based on project ID or repository

**Why GitHub Needs Extra Steps:**
1. **The Problem**: GitHub webhooks often just contain IDs, not useful information
2. **Getting More Data**: 
   - We need to ask GitHub's GraphQL API for details like item names and descriptions
   - Without this extra step, notifications would just say "Item 12345 was moved" instead of what actually happened
3. **How It Works**:
   - First, we save the webhook and get the extra data from GitHub
   - Then, we process it into a readable message
   - Finally, we send it to the right Discord channel

This approach lets us send helpful messages with real information instead of just ID numbers.

#### Zammad Integration
- Receives webhooks at `/webhooks/zammad/`
- Verifies signatures using HMAC-SHA1
- Processes ticket and article information
- Figures out what happened (new ticket, reply to ticket)
- Routes messages based on ticket group (billing, helpdesk)

### Channel Router
- Decides which Discord channel should receive messages
- Uses different routing rules for each source (GitHub, Zammad)
- Channel mappings are set in configuration
- Can be extended for new message sources in the future
