# Odds Autopsy

A forensic engine that tracks how World Cup betting odds moved during each match, finds the moments that caused the biggest shifts, maps them to match events, and produces a structured post match report anchored on Solana.

Built on TxLINE data from TxODDS.

## What it does

After each World Cup match, Odds Autopsy pulls every odds update TxLINE recorded during the game. It finds the moments where odds shifted the most, maps those shifts to the nearest score event, and measures how fast the market reacted. The result is a clean forensic report saved to disk and fingerprinted on Solana mainnet.

## Why it matters

Everyone builds prediction tools. Nobody builds audit tools. Odds Autopsy is the only system that answers: which events caused which moves, how fast did bookmakers react, and were those moves leading or lagging the action on the pitch? That is the data professional trading teams actually use internally.

## How it works

1. The fetcher pulls odds and score updates from TxLINE by epoch day and hour
2. The engine groups odds by market, finds significant shifts between consecutive updates, and maps each shift to the nearest score event by timestamp
3. The report builder saves a structured JSON file with the top 20 shifts and their match context
4. The anchor script hashes each report and writes a memo transaction to Solana mainnet as an immutable record
5. The dashboard loads all reports and displays them as interactive charts and tables

## TxLINE endpoints used

- GET /api/fixtures/snapshot
- GET /api/odds/updates/{epoch_day}/{hour}/0
- GET /api/scores/updates/{epoch_day}/{hour}/0

## Stack

- Python - data fetching, autopsy engine, report builder, Solana anchor
- React - dashboard with Recharts
- Solana mainnet - on chain report verification via memo transactions
- TxLINE - live World Cup odds and score data

## Running locally

1. Clone the repo
2. Add your TxLINE JWT and API token to .env
3. Run the backend server: python backend_server.py
4. Run the frontend: cd frontend && npm start
5. Generate reports: cd odds-autopsy && python backend/main.py
6. Anchor reports: python backend/anchor.py

## Structure
odds-autopsy/
odds-autopsy/
backend/
fetcher.py       pulls data from TxLINE
engine.py        finds shifts and maps to events
report_builder.py saves JSON reports
anchor.py        writes report hashes to Solana
main.py          runs the full pipeline
frontend/
src/App.js         React dashboard
reports/             generated JSON reports
backend_server.py    serves reports to the frontend

## Demo

Watch the demo video: [link]

Live dashboard: [link]