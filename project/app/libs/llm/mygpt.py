import os

from langchain_community.llms.yandex import YandexGPT

FOLDER_ID = os.getenv('FOLDER_ID')
IAM_TOKEN = os.getenv('IAM_TOKEN')

BIG_LLM = YandexGPT(
    model_name='yandexgpt',
    model_vesrsion='latest',
    folder_id=FOLDER_ID,
    iam_token=IAM_TOKEN,
    disable_request_logging=True,
    temparature=0
)


SMALL_LLM = YandexGPT(
    model_name='yandexgpt-lite',
    model_vesrsion='latest',
    folder_id=FOLDER_ID,
    iam_token=IAM_TOKEN,
    disable_request_logging=True,
    temparature=0
)
