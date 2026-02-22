from openai import AzureOpenAI
import aiohttp
import asyncio

from constants import HUB_API_KEY

# sample function using aiohttp (async programming)
async def fetch_top_headlines(category: str):
    params = {
                'category': category, 
                'token': HUB_API_KEY
              }
    try:
        async with aiohttp.ClientSession() as session:
            response = await session.get('https://finnhub.io/api/v11/news', params=params)
            response.raise_for_status()
            return await response.json()
    except Exception as e:
        print(f'fetch_top_headlines Error: {e}')
        return []
# # Get an Azure OpenAI chat client
# chat_client = AzureOpenAI(
#     api_version = "2024-12-01-preview",
#     azure_endpoint = open_ai_endpoint,
#     api_key = open_ai_key
# )

# # Initialize prompt with system message
# prompt = [
#     {"role": "system", "content": "You are a helpful AI assistant."}
# ]

# # Add a user input message to the prompt
# input_text = input("Enter a question: ")
# prompt.append({"role": "user", "content": input_text})

# # Additional parameters to apply RAG pattern using the AI Search index
# rag_params = {
#     "data_sources": [
#         {
#             "type": "azure_search",
#             "parameters": {
#                 "endpoint": search_url,
#                 "index_name": "index_name",
#                 "authentication": {
#                     "type": "api_key",
#                     "key": search_key,
#                 }
#             }
#         }
#     ],
# }

# # Submit the prompt with the index information
# response = chat_client.chat.completions.create(
#     model="<model_deployment_name>",
#     messages=prompt,
#     extra_body=rag_params
# )

# # Print the contextualized response
# completion = response.choices[0].message.content
# print(completion)

# ## vector based query.
# rag_params = {
#     "data_sources": [
#         {
#             "type": "azure_search",
#             "parameters": {
#                 "endpoint": search_url,
#                 "index_name": "index_name",
#                 "authentication": {
#                     "type": "api_key",
#                     "key": search_key,
#                 },
#                 # Params for vector-based query
#                 "query_type": "vector",
#                 "embedding_dependency": {
#                     "type": "deployment_name",
#                     "deployment_name": "<embedding_model_deployment_name>",
#                 },
#             }
#         }
#     ],
# }

 # Additional parameters to apply RAG pattern using the AI Search index
            # rag_params = {
            #     "data_sources": [
            #         {
            #             # he following params are used to search the index
            #             "type": "azure_search",
            #             "parameters": {
            #                 "endpoint": search_url,
            #                 "index_name": index_name,
            #                 "authentication": {
            #                     "type": "api_key",
            #                     "key": search_key,
            #                 },
            #                 # The following params are used to vectorize the query
            #                 "query_type": "vector",
            #                 "embedding_dependency": {
            #                     "type": "deployment_name",
            #                     "deployment_name": embedding_model,
            #                 },
            #             }
            #         }
            #     ],
            # }

##  Index Lookup tool to retrieve data from an index so that subsequent tools in the flow can use the results