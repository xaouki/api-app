# Maine SMS API Sender

A simple Windows desktop SMS sender built with Electron and the official MoceanAPI Node.js SDK.

## What it does

- Clean, simple Maine SMS API Sender interface
- MoceanAPI Token + Company / Sender Name only
- TXT / CSV recipient import
- Duplicate removal
- Test SMS
- Bulk campaign sending with a configurable minimum delay
- Pause / Resume / Stop
- Sent / Failed / Remaining / Success Rate counters
- Live activity log
- Export failed numbers
- International phone-number normalization
- Credentials are kept in memory during the session and are not written to the repository

## Requirements

- Windows 10/11
- Node.js 20+
- A MoceanAPI account and API Token

## Run locally

```bash
npm install
npm start
```

## Build Windows installer

```bash
npm run dist
```

The installer will be created in `dist/`.

## MoceanAPI setup

The application uses MoceanAPI's Node.js SDK and sends the standard SMS fields automatically:

- `mocean-from`
- `mocean-to`
- `mocean-text`

You only enter your MoceanAPI Token and Company / Sender Name in the app. No API URL, headers, field mapping, or API secret are required for the current token-based setup.

For US messaging, use an approved Mocean sender/number and follow Mocean's registration and content requirements.

## Responsible use

Send only to recipients who have authorized your messages. Follow MoceanAPI terms, carrier requirements, applicable privacy/telemarketing laws, and local messaging rules. This project does not bypass carrier filtering, registration, or provider restrictions.
