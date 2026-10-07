# Indian Broker API Setup Guide

## 1. Supported Broker Architectures
The system defines a unified `BrokerAdapter` abstract interface:
- `get_balance()`
- `get_positions()`
- `get_orders()`
- `place_order()`
- `modify_order()`
- `cancel_order()`

All broker implementations inherit from this base class.

---

## 2. Zerodha Kite Connect
1. Create a developer app on [kite.trade](https://kite.trade/).
2. Obtain your `API_KEY` and `API_SECRET`.
3. Set in `.env`:
   ```env
   ZERODHA_API_KEY=your_key
   ZERODHA_API_SECRET=your_secret
   ```
4. Authenticate each morning to generate your daily `ZERODHA_ACCESS_TOKEN`.

---

## 3. Angel One SmartAPI
1. Create an app on [smartapi.angelbroking.com](https://smartapi.angelbroking.com/).
2. Obtain your `API_KEY` and TOTP authenticator secret.
3. Configure in `.env`:
   ```env
   ANGEL_ONE_API_KEY=your_key
   ANGEL_ONE_CLIENT_CODE=your_client_code
   ANGEL_ONE_PASSWORD=your_password
   ANGEL_ONE_TOTP_KEY=your_totp_key
   ```
