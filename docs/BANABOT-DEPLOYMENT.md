# Bana Bot — Laravel Cloud deployment

## Deployment requirements
- Repository: `tekleabkidus-commits/Banabot`, branch `main`, application directory `/`.
- PHP 8.4.1 or newer; Laravel 12; Composer dependencies from `composer.lock`.
- PostgreSQL database, Redis/Valkey cache and queues, and an HTTPS Laravel Cloud application URL.
- A standalone Telegram bot token and webhook secret for Bana Bot, **not** the Liyubet bot credentials.

## Build and release
Laravel Cloud default Composer and NPM build commands can install dependencies and build Vite assets. Ensure `bootstrap/cache` and `storage/framework` exist in the source.

Deploy commands (run once for every release, against the attached database):

```bash
php artisan migrate --force
php artisan optimize:clear
```

Initial setup only (after connecting an empty database and setting strong credentials):

```bash
php artisan db:seed --force
```

Required credentials are read from Cloud environment settings; do not commit `.env`:
```dotenv
APP_NAME="Bana Bot"
APP_ENV=production
APP_DEBUG=false
APP_DISPLAY_TIMEZONE=Africa/Addis_Ababa
TELEGRAM_BOT_TOKEN=
TELEGRAM_BOT_USERNAME=
TELEGRAM_WEBHOOK_SECRET=
SEED_ADMIN_EMAIL=
SEED_ADMIN_PASSWORD=
CONVERSION_API_KEY=
```

Configure `DB_CONNECTION=pgsql`, `QUEUE_CONNECTION=redis`, `CACHE_STORE=redis`, `SESSION_DRIVER=redis` using Cloud-managed connection variables; ensure all queue processes connect to the same Redis.

## Background processing
Run an always-on worker for `telegram-interactive,telegram-broadcast,automation,default` (prefer independent workers per queue as explained in README). Configure Laravel's scheduler to execute every minute. Otherwise campaign broadcasts, webhooks and automations may not process.

Once `APP_URL` uses the final HTTPS URL and the *new* bot's credentials are set, run:
```bash
php artisan telegram:set-webhook
php artisan telegram:setup-menu
php artisan banabot:diagnose
```

Your backoffice is `https://<YOUR-LARAVEL-CLOUD-DOMAIN>/admin`. Change any initial seeded account credentials and enable MFA.

## Safety
This migration copies application source only. It does not copy player data, Telegram audience, files, production sessions, environment secrets, or the original Liyubet bot. The source repository is not modified. Never configure the new deployment with the old bot's webhook token.
