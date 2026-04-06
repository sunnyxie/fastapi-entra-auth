# Before running the sample:
#   pip install azure-ai-projects>=2.0.0
from azure.identity import DefaultAzureCredential
from azure.ai.projects.aio import AIProjectClient
from azure.ai.projects.models import PromptAgentDefinition
import asyncio

user_endpoint = "https://foundry-subs1.services.ai.azure.com/api/projects/proj-default-east2"

async def analysis_with_gpt5_chat(user_prompt : str, system_prompt: str = None):

    async with AIProjectClient(
        endpoint=user_endpoint,
        credential=DefaultAzureCredential(),
    ) as project_client:
        agent_name = "Agent951"
        model_deployment_name = "gpt-5-chat"

        # Creates an agent, bumps the agent version if parameters have changed
        agent = await project_client.agents.create_version(  
            agent_name=agent_name,
            definition=PromptAgentDefinition(
                    model=model_deployment_name,
                    instructions=system_prompt ##"You are a storytelling agent. You craft engaging one-line stories based on user prompts and context.",
                ),
        )

        openai_client = await project_client.get_openai_client()

        # Reference the agent to get a response
        response = await openai_client.responses.create(
            # input=[{"role": "user", "content": user_prompt}],
            # extra_body={"agent_reference": {"name": agent.name, "type": "agent_reference"}},
            model=model_deployment_name,
            input=[
                {"role": "system", "content": "You are a storytelling agent and specialize in investing. You craft engaging one-line stories."},
                {"role": "user", "content": user_prompt}
            ],
        )

        print(response)
        #print(f"Response output: {response.output_text}")


if __name__ == "__main__":
    asyncio.run(analysis_with_gpt5_chat("tell me a joke", "You are a storytelling agent. You craft engaging one-line stories based on user prompts and context"))