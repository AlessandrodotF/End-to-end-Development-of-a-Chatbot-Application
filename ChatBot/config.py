import os


AWS_REGION = os.getenv("AWS_REGION",None)
AWS_PROFILE = os.getenv("AWS_PROFILE",None)
MODEL_NAME = "us.anthropic.claude-haiku-4-5-20251001-v1:0"

TEMPERATURE = 0.0
MAX_TOKENS =1024