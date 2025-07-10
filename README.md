# I.N.S.I.G.H.T. Mark III - Cherry

**I.N.S.I.G.H.T. (Intelligent Networked Synthesis & Intelligence Gathering Heuristic Terminal)** is a powerful, lightweight Python tool for gathering and synthesizing intelligence from public news.

It features an intelligent synthesis engine that correctly identifies and groups media albums, an adaptive fetching mechanism, and a built-in API throttling defense system to ensure stable, long-term operation.

## Features

- **Dual Mission Profiles:**
  1.  **Deep Scan:** Retrieve the last 'N' logical posts from any single public channel.
  2.  **Daily Briefing:** Generate a consolidated intelligence briefing from multiple channels covering the last 'N' days.
- **Intelligent Album Synthesis:** Correctly understands and groups media albums (photos/videos sent together) into a single logical post with one caption.
- **Actionable Media Links:** Provides clean, direct links to view media associated with a post (`?single` parameter).
- **API Abuse Prevention:** Includes a built-in, two-stage throttling system to respect Telegram's API limits and automatically handle `FloodWaitError`.
- **Robust & Modular:** Built within a single class for clean, encapsulated, and extensible logic.

## Setup & Installation

**1. Prerequisites:**
- Python 3.8+
- An active Telegram account.

**2. Get Your Telegram API Credentials:**
- Go to [my.telegram.org](https://my.telegram.org) and log in.
- Click on "API development tools" and fill out the form.
- You will be given an `api_id` and `api_hash`. **Treat these like passwords.**

**3. Clone/Download the Project:**
- Get the project files onto your local machine.

**4. Create the `.env` Configuration File:**
- In the root of the project directory, create a file named `.env`.
- Add your API credentials to this file:
  ```dotenv
  TELEGRAM_API_ID=12345678
  TELEGRAM_API_HASH=your_api_hash_from_telegram_goes_here
  GEMINI_API_KEY=your_api_key
  ```