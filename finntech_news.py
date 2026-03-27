from datetime import datetime, timedelta
import sys
import time
from constants import MAX_NEWS_PER_REQUEST, TOP_HEADER_LINE_NUMBER, APT_5_ENDPOINT
import os
import finnhub
from dotenv import load_dotenv

from utils.generate_pdf import save_as_pdf

# This looks for a .env file and loads the variables into os.environ
load_dotenv()

HUB_API_KEY=os.getenv("HUB_API_KEY")
GEMINI_API_KEY=os.getenv("GEMINI_API_KEY")
GPT_5_KEY=os.getenv("GPT_5_KEY")  # from Azure Foundry


def fetch_finnhub_top_news(category: str = 'general'):
    """Fetch news articles for a given stock symbol from Finnhub API."""
    if not HUB_API_KEY:
        return None
    print('Fetching news from Finnhub...')
    finnhub_client = finnhub.Client(api_key=HUB_API_KEY)
    # You can also use 'merger', 'top news', etc.
    news = finnhub_client.general_news(category, min_id=0)

    formatted_news = []
    for item in news[:MAX_NEWS_PER_REQUEST]:
        formatted_news.append({
            "headline": item['headline'],
            "summary": item['summary'],
            "url": item['url'],
            "source": item['source']
        })
    return formatted_news

def get_company_news(symbol: str, maximum_count: int = 4):
    finnhub_client = finnhub.Client(api_key=HUB_API_KEY)
    to_date = datetime.now().strftime('%Y-%m-%d')
    from_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')

    try:
        news = finnhub_client.company_news(symbol, _from=from_date, to=to_date)
        print(news[:1])
        return news[:maximum_count]
    except Exception as e:
        print(f"Error fetching news for {symbol}: {e}")
        return []

from functools import lru_cache
@lru_cache(maxsize=12)
def fetch_tech_news(category: str = 'technology'):
    print(f"Fetching top {TOP_HEADER_LINE_NUMBER} news headlines for category: {category}" )
    headerlines = fetch_finnhub_top_news(category)

    # for i, line in enumerate(headerlines, 1):
    #     print(f"{i}. {line['headline']} - {line['source']}\n")
    #     if i >= TOP_HEADER_LINE_NUMBER:
    #         break
    return headerlines


from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential

agent_id = os.getenv("AZURE_EXISTING_AGENT_ID")
# Use DefaultAzureCredential if your app is authenticated via Managed Identity,  
project_endpoint = os.getenv("AZURE_EXISTING_AIPROJECT_ENDPOINT") # f"https://{agent_name}.projects.azure.com/agents/{agent_id}"

def analyze_headlines(headlines):  
    text_formated = ''
    for headline in headlines:
        if 'headline' in headline:
            text_formated += headline['headline'] + ' ; '
        if 'summary' in headline:
            text_formated += headline['summary'] + '\n'
    
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
        "finally add a three to four sentences investing summary before the JSON array;\n"
        "Headlines: \n" 
        + text_formated 
    )  ##  

    return prompt

# thread = LogSummaryAgent.threads.create()   not WORKING
# 1. Create the thread using the client, NOT the agent object
from azure.ai.agents import AgentsClient
from azure.ai.agents.models import ListSortOrder, MessageRole, MessageTextContent

# entry function to run to get the list of headlines that impact the market.
def run_agent_analysis():
    agent_client = AgentsClient(
        endpoint=project_endpoint,
        credential=DefaultAzureCredential()
    )

    agent = agent_client.create_agent(
        model='grok-4-1-fast-reasoning',
        name="agentClientNew",
        instructions="You are helpful financial adviser that make recommendations to individuals on investing, especially in tech sector",
    )
    agent_id = agent.id
    print(f'agent run created:  -- {agent.id}')

    thread = agent_client.threads.create()    
    # 2. Add a message to that thread
    chat_in_thread(agent_client, agent_id, thread.id)

    agent_client.delete_agent(agent_id=agent_id)

    # 3. get the messages
    return agent_client.messages.list(thread_id=thread.id, order=ListSortOrder.DESCENDING)
    

# using agent thrading chatting
def chat_in_thread(agent_client, agent_id, thread_id):
    message  = agent_client.messages.create(
        thread_id=thread_id,
        role="user",
        content="Can you help calculate Pow(3, 3)?"
    )

    message2 = agent_client.messages.create(
        thread_id=thread_id,
        role="user",
        content=analyze_headlines(fetch_tech_news('general'))
    )
    # 3. create run
    run = agent_client.runs.create(
        thread_id=thread_id,
        agent_id=agent_id, 
        model="grok-4-1-fast-reasoning",
    )

    while run.status != "completed":
        time.sleep(1)
        run = agent_client.runs.get(
            thread_id=thread_id,
            run_id=run.id
        )
        print(f"Run status: {run.id} {run.status} agent: {agent_id}")
        if run.status.lower() == "failed":
            print(f"Run failed! Error code: {run.last_error.code}")
            print(f"Error message: {run.last_error.message}")

    print(f'run completed {run.status}')

    return run

def foundry_gpt5_analysis(system_prompt: str = None, user_prompt: str = None):
    from openai import AzureOpenAI

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
                "content": user_prompt # "I am going to Paris, which places should I see?",
            }
        ],
        max_completion_tokens=120000,
        model=deployment
    )

    print(response.choices[0].message.content)   
    return response.choices[0].message.content
   

if __name__ == "__main__":
    _, args = sys.argv[0], sys.argv[1:]
    
    system_prompt = "Act as a Senior technology Analyst specializing in News Sentiment on the market. "
    analyzed_messages = foundry_gpt5_analysis(system_prompt, analyze_headlines(fetch_tech_news('general')))

    save_as_pdf(analyzed_messages, "./Outputs/Headline_Reports.pdf")
    print(' ** ' * 30)

    ### using agent do thread analysis. 
    responses = run_agent_analysis()

    agent_responses = []
    # we will iterate them and output only text contents.
    for data_point in responses:
        last_message_content = data_point.content[-1]
        if isinstance(last_message_content, MessageTextContent) and MessageRole.AGENT == data_point.role:
            print(f"{data_point.role}: {last_message_content.text.value}")
            agent_responses.append(last_message_content.text.value)
            
    #return agent_responses
 
    