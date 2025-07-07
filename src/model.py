import boto3
from langchain_aws import ChatBedrock
from botocore.config import Config
import warnings

warnings.filterwarnings("ignore")


class Model:
    def __init__(self):
        self.llm = self.get_model()

    def get_model(self):
        region = "us-east-1"
        config = Config(
            region_name=region,
            signature_version="v4",
            retries={
                "max_attempts": 3,
                "mode": "standard",
            },
        )
        bedrock_rt = boto3.client("bedrock-runtime", config=config)

        sonnet_model_id = "anthropic.claude-3-sonnet-20240229-v1:0"

        model_kwargs = {
            "max_tokens": 4096,
            "temperature": 0.0,
            "stop_sequences": ["Human"],
        }

        llm = ChatBedrock(
            client=bedrock_rt,
            model_id=sonnet_model_id,
            model_kwargs=model_kwargs,
        )

        return llm
