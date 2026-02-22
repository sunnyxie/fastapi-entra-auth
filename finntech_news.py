
import time
import json
from constants import HUB_API_KEY, MAX_NEWS_PER_REQUEST, TOP_HEADER_LINE_NUMBER
import finnhub

## https://ai-foundry-yx-feb.services.ai.azure.com/api/projects/proj-ai-analysis

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
from azure.ai.projects.models import AgentDefinition, PromptAgentDefinition
# from azure.ai.inference import ChatCompletionsClient    old not used any more
agent_id = 'asst_ZFqqWBIigtdwGEPpox0mCeH2'  
agent_name= 'Agent243' ## 'Agent3-openai'
# Use DefaultAzureCredential if your app is authenticated via Managed Identity,  
# or use an API key if available from the AI Foundry agent settings.  
project_endpoint = f"https://{agent_name}.projects.azure.com/agents/{agent_id}"  
## use new agent in EASTUS2, rg: rg-xiefang896-9622
project_endpoint= 'https://xiefang896-foundry-agen-resource.services.ai.azure.com/api/projects/xiefang896-foundry-agents'
project_client = AIProjectClient(
    endpoint=project_endpoint,
    credential=DefaultAzureCredential())


def analyze_headlines(headlines):  
    text_formated = ''
    for headline in headlines:
        if 'headline' in headline:
            text_formated += headline['headline'] + ' ; '
        if 'summary' in headline:
            text_formated += headline['summary'] + '\n'
    
    prompt = (  
        "Analyze the following NASDAQ headlines and assign an impact score from -10 to +10 based on its significance and impact on the stock market:\n\n"  
        "if any headline's impact is less or equal to 0, then don't return it. \n"
        "return the headlines in descending order of impact score: \n"
        "return the result strictly in JSON format: \n"
        "{\n"   
        ' "summary" : ...,\n'      
        ' "impact_score" : ###,\n'      
        ' "one_line_reason" : ...,\n' 
        ' "sentiment" : ...,\n'    
        "} \n"  
        "headlines: \n" 
        + text_formated 
    )  ## + "\n".join([ "\n".join( k + ': ' + v for k,v in headline.items() if k in ['headline', 'summary'] ) for headline in headlines])  

    return prompt
 #   print (prompt)

# chat_client = project_client.get_openai_client()
# project_client = AIProjectClient.from_connection_string(
#     credential=DefaultAzureCredential(),
#     conn_str=project_endpoint
# )
# agent_details = project_client.agents.get( agent_name='Agent3-openai')   not working
# print(f'Agent details: {json.dumps(agent_details)}')


######## Now switched to agentClient side.  resource : xiefang896-foundry-agents
# LogSummaryAgent = None
# try:
#     LogSummaryAgent = project_client.agents.create(
#         name=agent_name,
#         definition=agent_definition,
#         description="This agent helps me summarize my daily logs.",
#         metadata={"department": "engineering"}
#     )
# except:
# 2. Agents in Foundry are stateful. You need a 'Thread' for the conversation.
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
        model='gpt-5-chat',
        name="agentClientNew",
        instructions="You are helpful financial adviser that make recommendations to individuals on investing, especially in tech sector",
    )
    agent_id = agent.id
    print(f'agent run created:  -- {agent.id}')

    thread = agent_client.threads.create()    
    # 2. Add a message to that thread
    chat_in_thread(agent_client, agent_id, thread.id)

    agent_client.delete_agent(agent_id=agent_id)

    # 4. get the messages
    messages = agent_client.messages.list(thread_id=thread.id, order=ListSortOrder.DESCENDING)
    # we will iterate them and output only text contents.
    for data_point in messages:
        last_message_content = data_point.content[-1]
        if isinstance(last_message_content, MessageTextContent) and MessageRole.AGENT == data_point.role:
            print(f"{data_point.role}: {last_message_content.text.value}")
            return last_message_content.text.value


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
        model="gpt-5-chat",
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



    