# Getting started with the API (SMPP / HTTP)

Gatum offers both an HTTP REST API and an SMPP binding.

**HTTP API**
1. Generate an API key under **Settings → API keys**.
2. Send a `POST /v1/messages` request with `to`, `from` (Sender ID), and `text`.
3. The response returns a `message_id` you can use to query delivery status.

**SMPP**
1. Request SMPP credentials from **Settings → SMPP**.
2. Bind as a transceiver using the host, port, system_id, and password provided.
3. Submit messages with `submit_sm`; delivery receipts arrive as `deliver_sm`.

If your SMPP connection drops repeatedly, check your bind throttling and the
enquire_link interval before contacting support.
