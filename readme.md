# Execution

## Server
```bash
cd server
python -m src.main
```

### env
path: `server/src/.env`
```bash
NEWS_API_KEY=<NEWS_API_KEY>
THE_NEWS_API_KEY=<THE_NEWS_API_KEY>
UST_API_KEY=<UST_API_KEY>
HF_TOKEN=<HuggingFace_TOKEN>
SERVER_HOST="localhost"
SERVER_PORT=5000
CLIENT_IP="http://localhost:5173"
DEVICE="cpu"
```

## Client
```bash
cd client
npm run dev
```
- access localhost:5173

### env
path: `client/.env`
`VITE_SERVER_IP="http://localhost:5000"`

## News Fetching
- please refer to the --help option for detailed arguments
```bash
python -m src.utils.DataFetcher -e -hr 24 -m ust
```