# Google Cloud Setup Guide

This guide walks through setting up Google OAuth credentials required by the MCP server.

## Prerequisites

- A Google account
- Access to [Google Cloud Console](https://console.cloud.google.com/)

## Step 1: Create a Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click **Select a project** at the top of the page
3. Click **New Project**
4. Enter a project name (e.g., "Temporal Cortex Calendar")
5. Click **Create**

## Step 2: Enable the Google Calendar API

1. In your new project, go to **APIs & Services** > **Library**
2. Search for "Google Calendar API"
3. Click on **Google Calendar API**
4. Click **Enable**

## Step 3: Configure the OAuth Consent Screen

1. Go to **APIs & Services** > **OAuth consent screen**
2. Select **External** user type (unless you have a Google Workspace organization)
3. Fill in the required fields:
   - **App name**: Your app name (e.g., "My Calendar Assistant")
   - **User support email**: Your email
   - **Developer contact email**: Your email
4. Click **Save and Continue**
5. On the **Scopes** page, click **Add or Remove Scopes**
6. Add these scopes:
   - `https://www.googleapis.com/auth/calendar` (full calendar access)
   - `https://www.googleapis.com/auth/calendar.events` (event management)
7. Click **Save and Continue**
8. On the **Test users** page, add your Google email as a test user
9. Click **Save and Continue**

## Step 4: Create OAuth 2.0 Credentials

1. Go to **APIs & Services** > **Credentials**
2. Click **Create Credentials** > **OAuth client ID**
3. Select **Desktop app** as the application type
4. Enter a name (e.g., "Temporal Cortex MCP")
5. Click **Create**

You'll see a dialog with your **Client ID** and **Client Secret**. Copy both values — you'll need them in the next step.

> **Important**: As of 2025, Google only shows the Client Secret once at creation time. Download the JSON file or copy the values immediately.

## Step 5: Configure the MCP Server

You have two options for providing credentials to the MCP server:

### Option A: Environment Variables (Recommended)

Set these in your MCP client config:

```json
{
  "env": {
    "GOOGLE_CLIENT_ID": "123456789-abcdef.apps.googleusercontent.com",
    "GOOGLE_CLIENT_SECRET": "GOCSPX-your-secret-here"
  }
}
```

### Option B: JSON Credentials File

1. On the Credentials page, click the download icon next to your OAuth client
2. Save the JSON file to a secure location
3. Set the path as an environment variable:

```json
{
  "env": {
    "GOOGLE_OAUTH_CREDENTIALS": "/path/to/client_secret.json"
  }
}
```

The JSON file format is the standard Google Cloud Console download — the server reads `installed.client_id` and `installed.client_secret` from it automatically.

## Step 6: Authenticate

Run the auth command to complete the OAuth flow:

```bash
npx @temporal-cortex/cortex-mcp auth
```

This will:
1. Start a temporary local server on port 8085
2. Open your browser for Google OAuth consent
3. Exchange the authorization code for tokens (using PKCE for security)
4. Store tokens at `~/.config/temporal-cortex/credentials.json`

After authentication, the MCP server reuses stored tokens automatically. Tokens refresh in the background when they expire.

## Troubleshooting

### "Access blocked: This app's request is invalid"

Your OAuth consent screen may not be configured correctly. Ensure:
- You've added your email as a test user
- The Calendar API scopes are added
- The application type is "Desktop app"

### "Port 8085 is already in use"

Another application is using the default OAuth callback port. Set a different port:

```json
{
  "env": {
    "OAUTH_REDIRECT_PORT": "9090"
  }
}
```

### "The redirect URI in the request does not match"

The OAuth client must be of type "Desktop app", not "Web application". Web app clients require registered redirect URIs, while Desktop app clients accept any localhost port.
