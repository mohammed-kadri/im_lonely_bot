# Voice Channel Alone Notifier Bot

This Discord bot enhances voice channel management by notifying a designated channel when a user is alone in a voice channel for a configurable time period.  It helps server admins and community members keep track of users who might need company.

## Features

*   **Alone Notifications:** Sends a notification to a specified channel when a user remains alone in a voice channel for a set duration.
*   **Customizable Notification Period:**  Allows server administrators to configure the time period (in minutes) before a notification is sent using the `/set_notifications_period` command.
*   **Notification Pausing:** Provides commands (`/pause_notifications` and `/resume_notifications`) to pause and resume alone notifications for the server.
*   **User Exclusion:** Enables server administrators to exclude specific users from triggering alone notifications using the `/exclude_user` and `/include_user` commands.
*   **Notification Channel Setting:**  Lets server administrators designate the channel where notifications should be sent using the `/set_notifications_channel` command.

## Commands

*   `/set_notifications_period <minutes>`: Sets the time period (in minutes) before sending alone notifications.
*   `/pause_notifications`: Pauses alone notifications for the server.
*   `/resume_notifications`: Resumes alone notifications for the server.
*   `/exclude_user <user>`: Excludes a user from triggering alone notifications.
*   `/include_user <user>`: Includes a user in triggering alone notifications.
*   `/set_notifications_channel <channel_name>`: Sets the channel where alone notifications are sent.

## Setup

1.  **Clone the repository:** `git clone https://github.com/mohammed-kadri/im_lonely_bot`
3.  **Set environment variables:** Create a `.env` file in the project directory and set the `DISCORD_TOKEN` variable with your bot's token.  *Do not commit this file to your repository.*
4.  **Run the bot:** `im_lonely_bot.py`

## Deployment

This bot is designed to be deployed on a server environment.  A recommended approach is to use a virtual machine (e.g., Google Cloud Compute Engine, AWS EC2) or a containerized environment (Docker).  A process manager (e.g., `screen`, `tmux`, `pm2`) is essential to keep the bot running continuously.

**Example Deployment Steps (Google Cloud Compute Engine):**

1.  Create a Compute Engine instance.
2.  SSH into the instance.
3.  Clone the repository, install dependencies, and set up your virtual environment as described in the Setup section.
4.  Use `tmux` or `screen` to create a persistent session.
5.  Run your bot within the `tmux` or `screen` session.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request if you'd like to contribute to the project.


