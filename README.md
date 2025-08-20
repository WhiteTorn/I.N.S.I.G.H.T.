# I.N.S.I.G.H.T. Mark V - Frontier


Fully Dockered applicaiton to run with single command for production.


## Local Usage

For Telegram RSS use:
- https://github.com/xtrime-ru/TelegramRSS

(I reccommend using rss over standard api, because it is more stable and reliable)

For Twitter RSS use:
- https://github.com/sekai-soft/guide-nitter-self-hosting

## Installation

```
cp .env.example .env
```

Edit the `.env` file with actual credentials

## Docker Installation

From project root
docker build -t insight:mark-v .

Use either --env-file or mount .env; start both ports
docker run --rm \
  -p 5173:5173 -p 8000:8000 \
  --env-file .env \  # or: -v "$PWD/.env":/app/.env:ro
  insight:mark-v
