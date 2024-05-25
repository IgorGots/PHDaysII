from langchain.prompts import ChatPromptTemplate

sys_prompt = '''
Как большая языковая модель, ты должна помочь мне решить задачу составления промптов для другой языковой модели.
Я опишу область задачи, а ты должна написать промпт.
Твой ответ будет использоваться как запрос к другой большой языковой модели, поэтому не добавляй никакие комментарии.
В промпте перечисли требования к ответу модели.'''

prompt = ChatPromptTemplate.from_messages([
    ('system', sys_prompt),
    ('user', 'Напиши промпт для работы с данными {input}')
])

print(
    prompt.format(input='Security Operations Center (SOC)')
)
