from datetime import datetime, timedelta
import time
import asyncio
from constants import MAX_NEWS_PER_REQUEST, TOP_HEADER_LINE_NUMBER, APT_5_ENDPOINT
import os
import finnhub
from dotenv import load_dotenv

from logging_info import get_logger
from utils.generate_pdf import open_pdf, save_as_pdf

logger = get_logger(__name__)

# This looks for a .env file and loads the variables into os.environ
load_dotenv()

HUB_API_KEY=os.getenv("HUB_API_KEY")
GEMINI_API_KEY=os.getenv("GEMINI_API_KEY")
GPT_5_KEY=os.getenv("GPT_5_KEY")  # from Azure Foundry


async def fetch_finnhub_top_news(category: str = 'general'):
    """Fetch news articles for a given stock symbol from Finnhub API."""
    if not HUB_API_KEY:
        return None
    logger.info('Fetching news from Finnhub...')
    finnhub_client = finnhub.Client(api_key=HUB_API_KEY)
    # You can also use 'merger', 'top news' as category, etc.
    try:
        news = await asyncio.to_thread(finnhub_client.general_news, category, min_id=0)
        # news =finnhub_client.general_news(category, min_id=0)

        formatted_news = []
        for item in news[:MAX_NEWS_PER_REQUEST]:
            formatted_news.append({
                "headline": item['headline'],
                "summary": item['summary'],
                "url": item['url'],
                "source": item['source']
            })
        return formatted_news
    except Exception as e:
        logger.error(f"Error fetching Finnhub news: {e}")
        return None 


async def get_company_news(symbol: str, maximum_count: int = 4):
    finnhub_client = finnhub.Client(api_key=HUB_API_KEY)
    to_date = datetime.now().strftime('%Y-%m-%d')
    from_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')

    try:
        # finnhub-python is synchronous, wrap in thread to avoid blocking event loop
        news = await asyncio.to_thread(finnhub_client.company_news, symbol, _from=from_date, to=to_date)
        return news[:maximum_count]
    except Exception as e:
        logger.error(f"Error fetching news for {symbol}: {e}")
        return []

from functools import lru_cache
@lru_cache(maxsize=2)
async def fetch_tech_news(category: str = 'technology'):
    logger.info(f"Fetching top {TOP_HEADER_LINE_NUMBER} news headlines for category: {category}" )
    return await fetch_finnhub_top_news(category)


from azure.identity import DefaultAzureCredential

agent_id = os.getenv("AZURE_EXISTING_AGENT_ID")
# Use DefaultAzureCredential if your app is authenticated via Managed Identity,  
project_endpoint = os.getenv("AZURE_EXISTING_AIPROJECT_ENDPOINT") # f"https://{agent_name}.projects.azure.com/agents/{agent_id}"

def analyze_headlines(headlines):  
    lines = []
    for headline in headlines:
        if 'headline' in headline:
            lines.append(f"{headline['headline']} ; ")
        if 'summary' in headline:
            lines.append(f"{headline['summary']}\n")
    text_formated = "".join(lines)

    prompt = (  
        "Analyze the following Technology headlines and assign an impact score from -10 to +10 based on its significance and impact on the stock market:\n\n"  
        "if any headline's impact is less or equal to 0, then don't return it. \n"
        "return the headlines in descending order of impact score: \n"
        "give your brief reason on the key field 'one_line_reason' \n"
        "return the result strictly in JSON format (remove parentheses for easy reading): \n"
        "{\n"   
        ' summary : ...,\n'      
        ' impact_score : ###,\n'      
        ' one_line_reason : ...,\n' 
        ' sentiment : ...,\n'    
        "} \n"  
        "finally add a three to four sentences of investing and sentiment summary before the JSON array;\n"
        "and try to name a sector, include the crypto sector, that might outperform in the next 1 to 2 days (it's not a investment strategy.) . "
        "Headlines: \n" 
        + text_formated 
    )  ##  

    return prompt

# thread = LogSummaryAgent.threads.create()   not WORKING
# 1. Create the thread using the client, NOT the agent object
from azure.ai.agents.aio import AgentsClient
from azure.ai.agents.models import ListSortOrder, MessageRole, MessageTextContent

# entry function to run to get the list of headlines that impact the market.
async def run_agent_analysis():
    async with AgentsClient(
        endpoint=project_endpoint,
        credential=DefaultAzureCredential()
    ) as agent_client:

        agent = await agent_client.create_agent(
            model='grok-4-1-fast-reasoning',
            name="agentClientNew",
            instructions="You are helpful financial adviser that make recommendations to individuals on investing, especially in tech sector",
        )
        agent_id = agent.id
        logger.info(f'agent run created:  -- {agent.id}')

        thread = await agent_client.threads.create()    
        # 2. Add a message to that thread
        await chat_in_thread(agent_client, agent_id, thread.id, model_name="grok-4-1-fast-reasoning")

        await agent_client.delete_agent(agent_id=agent_id)

        # 3. get the messages and extract text for the caller (FastAPI or Script)
        # return agent_client.messages.list(thread_id=thread.id, order=ListSortOrder.ASCENDING)
        
        messages = []
        async for msg in agent_client.messages.list(thread_id=thread.id, order=ListSortOrder.ASCENDING):
            if msg.role == MessageRole.AGENT:
                # for content in msg.content:
                #     if isinstance(content, MessageTextContent):
                messages.append(msg)
        return messages
    

# using agent thrading chatting
async def chat_in_thread(agent_client, agent_id, thread_id, model_name="grok-4-1-fast-reasoning"):
    await agent_client.messages.create(
        thread_id=thread_id,
        role="user",
        content="Can you tell me the top 2 news or headlines in the Agentic AI World (be frontier, they might or might not impact the market)?"
    )

    await agent_client.messages.create(
        thread_id=thread_id,
        role="user",
        content="Just tell me a joke on technology or investing field."
    )

    await agent_client.messages.create(
        thread_id=thread_id,
        role="user",
        content=analyze_headlines(await fetch_tech_news('general'))
    )
    #  create the run
    run = await agent_client.runs.create(
        thread_id=thread_id,
        agent_id=agent_id, 
        model=model_name,
    )

    while run.status != "completed":
        await asyncio.sleep(1)
        run = await agent_client.runs.get(
            thread_id=thread_id,
            run_id=run.id
        )
        logger.info(f"Run status: {run.id} {run.status} agent: {agent_id}")
        if run.status.lower() == "failed":
            logger.error(f"Run failed! Error code: {run.last_error.code}")
            logger.error(f"Error message: {run.last_error.message}")

    logger.info(f'run completed. Status: {run.status}')
    return run

def foundry_gpt5_analysis(system_prompt: str = None, user_prompt: str = None):
    from openai import  AzureOpenAI # AsyncAzureOpenAI  

    endpoint = "https://foundry-subs1.cognitiveservices.azure.com/"
    model_name = "gpt-5"
    deployment = "gpt-5"  

    api_version = "2024-12-01-preview"

    client = AzureOpenAI(
        api_version=api_version,
        azure_endpoint=endpoint,
        api_key=GPT_5_KEY,
    )

    response = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": user_prompt 
            }
        ],
        max_completion_tokens=120000,
        model=deployment
    )

    print(response.choices[0].message.content)   
    return response.choices[0].message.content

async def do_gpt5_analysis():
    system_prompt = "Act as a Senior technology Analyst specializing in News Sentiment on the market. "
    # Await the async fetch
    raw_news = await fetch_tech_news('general')

    formatted_prompt = analyze_headlines(raw_news)
    analyzed_messages = foundry_gpt5_analysis(
        system_prompt, 
        formatted_prompt
        )
    print("GPT 5 Run ended", ' ** ' * 30)   
    return analyzed_messages


def parse_agent_response(response_raw):
    agent_responses = []
    # we will iterate them and output only text contents.
    for data_point in response_raw:
        last_message_content = data_point.content[-1]
        if isinstance(last_message_content, MessageTextContent) and MessageRole.AGENT == data_point.role:
            print(f"{data_point.role}: {last_message_content.text.value}")
            agent_responses.append(last_message_content.text.value)

    return agent_responses


if __name__ == "__main__":
    logger = get_logger(__name__)
    #analyzed_messages = asyncio.run(do_gpt5_analysis())
    analyzed_messages = ''

    ### using agent do thread analysis. 
    responses = asyncio.run(run_agent_analysis())

    agent_responses = parse_agent_response(responses)
    sentiment_summary = ''
    if len(agent_responses) > 0:
        TRUNCATE_MAX_FROM_AGENT = 2800
        # deliberately appending the beginning part of the foundry agent's responses.  
        sentiment_summary = agent_responses[0][0:TRUNCATE_MAX_FROM_AGENT] if len(agent_responses) > 0 else '' 

    file_path = os.path.join("./Outputs", f"Headline_Reports_{time.strftime('%Y-%m-%d_%H-%M-%S')}.pdf")
    save_as_pdf(analyzed_messages + "\n" + sentiment_summary, file_path)
    logger.info(f'pdf file saved: {file_path}')

    open_pdf(os.path.abspath(file_path))


 
    