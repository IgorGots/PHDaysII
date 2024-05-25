import re

from collections import defaultdict

from langchain.callbacks.base import BaseCallbackHandler
from langchain_core.messages import AIMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.tools import tool

from libs import db, text
from libs.my_company import soar, siem, alert
from app.libs.llm import mygpt
from libs.prompts.chat import alert_prompt, chat_prompt
from libs.prompts.rephrase import simple_prompt
from libs.prompts.verdict import verdict_prompt

import libs.logger as logger
log = logger.setup_applevel_logger()


class CustomHandler(BaseCallbackHandler):
    def __init__(self, **kwargs):
        self.kwargs = kwargs

    def on_llm_start(
        self, serialized, prompts, **kwargs
    ):
        formatted_prompts = "\n".join(prompts)
        with open('/vtmp/prompt.prompt', 'w') as prompt:
            prompt.write(formatted_prompts)

        # return formatted_prompts


def rephrase_query(msg: str) -> str:
    """Reformulates the user's question using llm

    Args:
        msg (AIMessage): message

    Returns:
        Runnable: Structure for langchain
    """
    log.info(f'Got message: {msg}')

    chain = (
        simple_prompt
        | mygpt.SMALL_LLM
        | StrOutputParser()
    )

    answer = chain.invoke({"question": msg})

    log.info(f'Result: {answer}')
    return answer


def format_docs(docs, max_size=12000):
    content = ''
    for doc in docs:
        if len(content) + len(doc.page_content) + 2 > max_size:
            break
        content += doc.page_content + '\n\n'

    return content


@tool
def chat(message: str) -> str:
    """Отвечает на общие вопросы, связанные с работой SOC и СИБ. Не предназначен для анализа карточек алертов в очереди ALERTS.

    Args:
        message (TgMessage): Сообщение пользователя

    Returns:
        AIMessage: Ответ модели
    """

    rdb = db.get_db()

    retriever = rdb.as_retriever(search_kwargs={
        'k': 20,
        'where_str': '''metadata.source NOT LIKE '%alertcomments_%' '''
    })

    rag_chain = (
        {"context": retriever | format_docs, "question": rephrase_query}
        | chat_prompt
        | mygpt.BIG_LLM
        | StrOutputParser()
    )

    answer = rag_chain.invoke(
        message,
        config={"callbacks": [CustomHandler(message=message)]}
    )

    return answer


@tool
def alert_answer(message: str) -> str:
    """Анализирует тикет в очереди ALERTS и предполагает, что может ответить сотрудник SOC

    Args:
        message (TgMessage): _description_

    Returns:
        AIMessage: _description_
    """
    match = re.search(r'ALERT-\d+', message)

    if match:

        ticket = soar.stget_ticket_by_key(key=match.group(0))
        alert_name, ticket_desc, ticket_comments = soar.get_alert(ticket)
        ticket_desc = text.clean_text(ticket_desc)

        # remove trailing SOC comments
        for i in range(len(ticket_comments)-1, 0, -1):
            if ticket_comments[i]['user'] not in ['SOC']:
                break
            else:
                del ticket_comments[i]

        current_comments = '\n'.join([f'''{c['user']}: {text.clean_text(c['text'])}''' for c in ticket_comments])
        alert_desc = text.clean_text(soar.get_description(name=alert_name))

        rdb = db.get_db()
        retriever = rdb.as_retriever(search_kwargs={
            'k': 3,
            'where_str': f'''metadata.source LIKE '%alertcomments_%' AND metadata.source LIKE '%{alert_name}%' AND dist < 7'''
        })
        docs = retriever.invoke(current_comments)
        past_comments = ''
        for index, doc in enumerate(docs):
            past_comments += f'''## Диалог{index+1}:\n{doc.page_content}\n\n'''
        past_comments = text.clean_text(past_comments)

        rag_chain = alert_prompt | mygpt.BIG_LLM | StrOutputParser()

        answer = rag_chain.invoke(
            {
                'past_analysis': past_comments,
                'description': alert_desc,
                'alert_body': ticket_desc,
                'current_comments': current_comments
            },
            config={"callbacks": [CustomHandler(description=alert_desc, alert_body=ticket_desc)]}
        )

        return answer

    else:
        return AIMessage(
            content='Не нашел подстроку ALERT- в запросе. Не понимаю как помочь.'
        )


@tool
def alert_verdict(message: str) -> AIMessage:
    """Анализирует тикет в очереди ALERTS и оценивает является ли связанный с ним алерт TruePositive или FalsePositive

    Args:
        message (TgMessage): _description_

    Returns:
        AIMessage: _description_
    """
    match = re.search(r'ALERTS-\d+', message)

    if match:
        ticket_key = match[0]
        ticket = soar.get_ticket_by_key(ticket_key)

        query = 'git ticket fields'

        results = siem.query(query)

        if len(results) == 1:

            current_alert = alert.fields_process(results[0])

            alerts_str = ''
            verdicts = defaultdict(int)
            alerts = alert.get_past_alerts(ticket.alert_name, exclude=[ticket_key])
            for _alert in alerts:
                verdict = _alert.pop('alert_verdict')
                verdicts[verdict] += 1

                if verdicts[verdict] <= 6 and len(alerts_str) < 8000:
                    _alert.pop('alert_classification')
                    alerts_str += f'Параметры: {_alert}\nВердикт: {verdict}\n\n'

            chain = (verdict_prompt | mygpt.BIG_LLM | StrOutputParser())
            answer = chain.invoke(
                {'examples': alerts_str, 'alert': current_alert},
                config={"callbacks": [CustomHandler(message=message)]}
            )

            return answer

        return AIMessage(
            content='Что-то пошло не так'
        )


def compare_answers(question: str, good_answer: str, generated_answer: str, language: str = 'russian') -> dict:
    from libs.prompts.evaluation import evaluation_prompt_template

    chain = evaluation_prompt_template | mygpt.BIG_LLM | StrOutputParser()

    answer = chain.invoke(
        {
            'question': question,
            'response': generated_answer,
            'reference_answer': generated_answer
        }
    )

    return answer
