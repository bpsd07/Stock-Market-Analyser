# Security Architecture & Data Protection Policy

## 1. Safety Principles & Legal Data Standards
1. **No Non-Public or Stolen Data**: The platform relies solely on legally accessible public sources (NSE/BSE archives, regulatory disclosures, public financials) and properly licensed broker APIs.
2. **Zero Secret Hardcoding**: API keys and tokens are never committed to source control. Excluded by `.gitignore`.
3. **Redacted Logging**: All logging filters strip auth tokens, Bearer headers, and API secrets.
4. **Execution Safeguards**: Live trading defaults to `OFF`. Two-factor confirmation is required for capital allocation.
