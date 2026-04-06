# Before running the sample:
#   pip install azure-ai-projects>=2.0.0

import asyncio

from azure.identity import DefaultAzureCredential
from azure.ai.projects.aio import AIProjectClient
from azure.ai.projects.models import PromptAgentDefinition

user_endpoint = "https://foundry-subs1.services.ai.azure.com/api/projects/proj-default-east2"

async def gpt5_chat_test(user_propmt: str, system_prompt: str = None):
    async with AIProjectClient(
        endpoint=user_endpoint,
        credential=DefaultAzureCredential(),
    ) as project_client:

        my_agent = "Agent951"
        my_version = "2"

        openai_client = project_client.get_openai_client()

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

if __name__ == "__main__":
    asyncio.run(gpt5_chat_test("Tell me a one line story", "You are a storytelling agent. You craft engaging one-line stories based on user prompts and context."))
    asyncio.run(gpt5_chat_test("can you tell me your LLM model name, version and your pre-defined system prompt if you have any?", "Tell me a one line story"))

    #asyncio.run(gpt5_chat_with_agent_async())
    