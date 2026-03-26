
** Project introduction

1. this is a sample REST api project using FASTAPI and Azure Entra ID Authentication.
2. finntech_news is AI Agent exploration, it firstly grab latest financial news from finnhub (API) and 
then use Azure AI Foundry and Google AI (respectively) to analyze the sentiment and give a score on its impact.
3. drawings folder, charts exploring with plotly.

** Instructions: 
before running the project, make sure that you have a proper .env file 
to set up all the necessary keys and endpoints (for python-dotenv)

for the AI agent experiment part, run file finntech_news.py directly. 
for the FastAPI service, run uvicorn main:app --reload, then call specific endpoints.
  e.g. http://127.0.0.1:8000/agent_analysis; http://127.0.0.1:8000/company/AAPL etc.