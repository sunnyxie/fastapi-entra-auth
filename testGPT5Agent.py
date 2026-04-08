# Before running the sample:
#   pip install azure-ai-projects>=2.0.0

import asyncio
import os

from azure.identity import DefaultAzureCredential
from azure.ai.projects.aio import AIProjectClient
from azure.ai.projects.models import PromptAgentDefinition
from dotenv import load_dotenv

from finntech_news import chat_in_thread, parse_and_save_pdf

user_endpoint = "https://foundry-subs1.services.ai.azure.com/api/projects/proj-default-east2"

async def gpt5_chat_test(user_propmt: str, system_prompt: str = None):
    async with AIProjectClient(
        endpoint=user_endpoint,
        credential=DefaultAzureCredential(),
    ) as project_client:

        my_agent = "Agent951"
        my_version = "2"

        openai_client = project_client.get_openai_client()
      
        # Create a thread
        thread = await openai_client.agents.get()
        thread_id = thread.id
        # Reference the agent to get a response
        response = await openai_client.responses.create(
            input=[{"role": "user", "content": user_propmt}],
            extra_body={"agent_reference": {"name": my_agent, "version": my_version, "type": "agent_reference"}},
        )

        print(f"###  output: {response.output_text}")


## FINAL Working version with async
async def gpt5_chat_with_agent_async():
    from azure.identity import DefaultAzureCredential

    my_endpoint = "https://foundry-subs1.services.ai.azure.com/api/projects/proj-default-east2"

    async with AIProjectClient(
        endpoint=my_endpoint,
        credential=DefaultAzureCredential(),
    ) as project_client:

        my_agent = "Agent951"
        my_version = "2"

        openai_client = project_client.get_openai_client()

        # Reference the agent to get a response
        response = await openai_client.responses.create(
            input=[{"role": "user", "content": "Tell me what you can help with."}],
            extra_body={"agent_reference": {"name": my_agent, "version": my_version, "type": "agent_reference"}},
        )

        print(f"###  output: {response.output_text}")

from azure.ai.agents.aio import AgentsClient
from azure.ai.agents.models import ListSortOrder, MessageRole, MessageTextContent

async def run_agent_gpt5_analysis():
    async with AgentsClient(
        endpoint="https://foundry-subs1.services.ai.azure.com/api/projects/proj-default-east2",
        credential=DefaultAzureCredential()
    ) as agent_client:

        agent = await agent_client.create_agent(
            model='gpt-5-chat',
            name="Agent951aa",
            instructions="You are helpful financial adviser that make recommendations or advice to individuals on investing, especially in tech & crypto sector.",
        )
        agent_id = agent.id
        # logger.info(f'agent run created:  -- {agent.id}')

        thread = await agent_client.threads.create()    
        # 2. Add a message to that thread
        await chat_in_thread(agent_client, agent_id, thread.id, model_name="gpt-5-chat")

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
        


if __name__ == "__main__":
    load_dotenv()
    project_endpoint = os.getenv("AZURE_EXISTING_AIPROJECT_ENDPOINT")

    msg = asyncio.run(run_agent_gpt5_analysis())
    parse_and_save_pdf("", msg)

    # asyncio.run(gpt5_chat_test("Tell me a one line story", "You are a storytelling agent. You craft engaging one-line stories based on user prompts and context."))
    # asyncio.run(gpt5_chat_test("can you tell me your LLM model name, version and your pre-defined system prompt if you have any?", "Tell me a one line story"))

    #asyncio.run(gpt5_chat_with_agent_async())
    