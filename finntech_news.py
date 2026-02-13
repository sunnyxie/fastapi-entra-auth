
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
# from azure.ai.inference import ChatCompletionsClient    old not used any more
agent_id = 'asst_ZFqqWBIigtdwGEPpox0mCeH2'
agent_name='Agent3-openai'
# Use DefaultAzureCredential if your app is authenticated via Managed Identity,  
# or use an API key if available from the AI Foundry agent settings.  
endpoint = f"https://{agent_name}.projects.azure.com/agents/{agent_id}"  
## use new agent in EASTUS2
endpoint= 'https://xiefang896-foundry-agen-resource.services.ai.azure.com/api/projects/xiefang896-foundry-agents'
project_client = AIProjectClient(
    endpoint=endpoint,
    credential=DefaultAzureCredential())

# chat_client = project_client.inference.get_chat_completions_client()
chat_client = project_client.get_openai_client()

def analyze_headlines(headlines):  
    text_formated = ''
    for headline in headlines:
        if 'headline' in headline:
            text_formated += headline['headline'] + ' ; '
        if 'summary' in headline:
            text_formated += headline['summary'] + '\n'
    
    prompt = (  
        "Analyze the following NASDAQ headlines and assign an impact score from -10 to +10 based on its significance:\n\n"  
        "return the result strictly in JSON format: \n"
        "{\n"   
        ' "impact_score" : ###,\n'      
        ' "one_line_reason" : ...,\n' 
        ' "sentiment" : ...,\n'    
        "} \n"  
        "headlines: \n" 
        + text_formated 
    )  ## + "\n".join([ "\n".join( k + ': ' + v for k,v in headline.items() if k in ['headline', 'summary'] ) for headline in headlines])  

    print (prompt)

    try:
        deployment_name = "gpt-5-chat" #"gpt-4o"
        response = chat_client.chat.completions.create(messages=[{"role": "user", "content": prompt}], 
                                model=deployment_name,
                                response_format="json")  
        print(' ** ' * 21)
        print(' ## empty choices' if response.choices is None or response.choices == [] else response.choices[0].message)
        return json.loads(response.choices[0].message.content) 
    except Exception as e:
        return {"error": 'AI Foundry communication error: ' + str(e)}
    