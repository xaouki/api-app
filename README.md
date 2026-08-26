# SMS API Sender

A simple Windows desktop application for sending SMS through a user's own REST API. The app is provider-agnostic: the user supplies the HTTPS endpoint, authentication, request field names, message and recipient list.

## Features

- Generic HTTPS REST API support (POST, PUT, PATCH)
- Bearer token or custom API-key header authentication
- JSON or form-urlencoded request bodies
- Custom recipient/message/sender field names
- Extra JSON fields
- TXT/CSV recipient import
- Duplicate removal
- Test send
- Bulk sending with configurable delay/rate control
- Pause, resume and stop
- Sent/failed/remaining counters
- Export failed recipients
- Local profile storage (credentials are kept on the local machine and are never committed by the app)

## Run locally

Install Node.js 20+ and then:

```bash
npm install
npm start
```

## Build Windows installer

```bash
npm run dist
```

The generated installer is placed in `dist/`.

## Request example

For an API expecting:

```json
{"to":"+14155550100","message":"Hello"}
```

use API URL = your provider endpoint, method = POST, content type = JSON, recipient field = `to`, message field = `message`.

The application intentionally does not contain a provider API key or a hard-coded SMS service. Users are responsible for authorization, consent, provider terms, rate limits, and applicable messaging laws.
