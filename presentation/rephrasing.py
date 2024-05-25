import os
from langchain.prompts import ChatPromptTemplate
from langchain_community.llms import YandexGPT

FOLDER_ID = os.getenv("FOLDER_ID")
IAM_TOKEN = os.getenv("IAM_TOKEN")

QUESTION = 'Как залочить учетку человека на хосте?'

slang_dict = {'учетка': 'учетная запись',
    'человек': 'пользователь',
    'хост': 'компьютер сотрудника или сервер компании'}

sys_prompt = 'Переформулируй запрос. Необходимо избавиться от сленга. Ничего не добавляй от себя.\nСленг:\n' \
    + '\n'.join([f'* {key} - {value}'for key, value in slang_dict.items()])

prompt = ChatPromptTemplate.from_messages([('system', sys_prompt), ('user', '{question}')])
print( prompt.format(question=QUESTION) + '\n---\n')

llm = YandexGPT(
    model_name='yandexgpt-lite',
    folder_id=FOLDER_ID,
    iam_token=IAM_TOKEN,
    temparature=float(0)
)
chain = prompt | llm

print(f'''Rephrased question: {chain.invoke({'question': QUESTION})}''')
