# BCM SLS RFP Dashboard

A responsive React + Vite landing page for account and RFP portfolio tracking.

## Run locally

```bash
npm install
npm run dev
```

Build for production with `npm run build`.

## Data

- `AccountList.md` and `AccountsList.md` are supported interchangeably; entries from both are merged and deduplicated for the Account Name dropdown.
- `RFPStatus.md` supplies the repeated RFP cards and their metadata.

The Markdown files are imported as raw text and parsed in the browser. Keep their current list/table structures when replacing the sample data.

## Customer RFP documentation

Selecting an account loads files live from its corresponding subfolder under `Customer RFP Documentation` (for example, `Customer RFP Documentation/Bank 1`). Files do not need to repeat the account name. Each file exposes GitHub view and download links.

## Behavior

- Winzone ID accepts integers and is intentionally not externally validated yet.
- Service-line selections are maintained independently for each RFP.
- Save draft stores the current form state in browser local storage.
