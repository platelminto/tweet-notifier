# tweet-notifier
Get pushover notifications when specific twitter accounts tweet.

This is aimed at getting the notifications quickly (e.g. every minute). If this doesn't matter to you, maybe just use IFTTT (which has ~hour resolution, 1 account followed), or Zapier (~15 minutes, 5 accounts).

## Requirements

- [Twitter API access](https://developer.twitter.com/en/portal/dashboard) (Free? Docs say it costs now, but I'm still using it perfectly fine. Weird.)
- [Pushover API access](https://pushover.net/) (Requires a one-time $5 payment. 30-day free trial.)

## Installation

Install requirements:

`pip install -r requirements.txt`

Copy `config.json.example` and `auth.json.example` to `config.json` and `auth.json`, respectively.

### `auth.json`

- `twitter.bearer`: A Twitter API application bearer token. You receive one once you create an app. You will easily fit within the free tier's limits.
- `pushover.app_token`: A Pushover API application token. You also get one of these once you create a Pushover app, and can view it when logged in [here](https://pushover.net/).
- `pushover.user_key`: Your Pushover user (or group) token.

### `config.json`

- `twitter.users`: list of Twitter handles of users you want to receive tweet notifications from.
- `pushover.device`: device name (as set in your Pushover settings) to send notifications to. Leave blank to send to all devices.

## Usage

Run `main.py`. On first run, nothing will happen. Each subsequent run, for every account specified in `config.json`, any tweets not previously seen will be sent to Pushover.

Run periodically on a VPS to avoid downtime. 
