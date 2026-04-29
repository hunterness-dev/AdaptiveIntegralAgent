# Adaptive Integral Agent

Monte Carlo integration tool with AI explanations, interactive plots, and PDF reports.

## Features

- 1D and 2D Monte Carlo integration
- Convergence plots, error analysis
- AI explanations (simple, scientific, IEEE style) using Ollama/Llama3
- PDF report generation
- Send reports via Telegram, Gmail, Google Drive

## Installation

### 1. Clone the repository
```bash
git clone https://github.com/hunterness-dev/AdaptiveIntegralAgent.git
cd AdaptiveIntegralAgent
```

### 2. Install Python dependencies
```bash
pip install -r requirements.txt
```

### 3. Install Ollama (for AI explanations)

#### Windows
- Download `OllamaSetup.exe` from [ollama.com](https://ollama.com)
- Run the installer
- Open Command Prompt and run:
```bash
ollama pull llama3
```

#### macOS / Linux
```bash
curl -fsSL https://ollama.com/install.sh | sh
ollama pull llama3
```

### 4. Start Ollama service
Open a separate terminal and run:
```bash
ollama serve
```

## Run the App

```bash
streamlit run UI.py
```

Then open your browser at `http://localhost:8501`

## Project Structure

| File | Description |
|------|-------------|
| UI.py | Streamlit interface |
| agent.py | Monte Carlo integrator |
| analyzer.py | Error analysis and plots |
| explainer.py | AI explanation with Ollama |
| senders.py | Telegram, Gmail, Drive sender |
| config.py | Tokens and passwords (DO NOT SHARE) |

## Usage

1. Select dimension (1D or 2D)
2. Enter function (e.g., `x**2 + y**2`)
3. Set integration bounds
4. Choose number of samples (500-10000)
5. Click "Run Analysis"
6. View convergence plots and AI explanations
7. Download PDF report or send via Telegram/Gmail/Drive

## Examples

| Function | Bounds | Approximate Result |
|----------|--------|-------------------|
| x**2 | [0, 1] | 0.333 |
| sin(x) | [0, π] | 2.000 |
| exp(-x**2) | [-2, 2] | 1.764 |
| x**2 + y**2 | [0,1] × [0,1] | 0.667 |

## Sending Reports

### Telegram
- Create a bot via [@BotFather](https://t.me/BotFather)
- Copy the Bot Token
- Get your Chat ID
- Enter in the app sidebar

### Gmail
- Enable 2-Factor Authentication on your Google account
- Generate an "App Password"
- Enter email and app password in the app

### Google Drive
- Place `service_account.json` in the project root
- Enable Drive API in Google Cloud Console

## Security

**IMPORTANT:** Do NOT commit these files to GitHub:
- `config.py` (contains tokens)
- `service_account.json` (Google service account key)
- `.env` (environment variables)

Add them to `.gitignore`:
```
config.py
service_account.json
.env
__pycache__/
*.pyc
```

## Requirements

Create `requirements.txt`:
```
streamlit>=1.28.0
numpy>=1.24.0
sympy>=1.12.0
plotly>=5.17.0
reportlab>=4.0.0
requests>=2.31.0
google-api-python-client>=2.108.0
google-auth-httplib2>=0.1.1
google-auth-oauthlib>=1.1.0
```

## Troubleshooting

### Ollama connection error
Make sure `ollama serve` is running before starting the app.

### Invalid function error
Use valid Python syntax: `x**2` (not `x^2`), `sin(x)`, `exp(x)`, `log(x)`

### No valid samples
Check that your function returns finite values within the bounds.

## License

MIT

## Author

**Hunterness Dev**

GitHub: [@hunterness-dev](https://github.com/hunterness-dev)