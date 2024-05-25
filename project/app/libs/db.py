import os

from langchain_community.vectorstores import Clickhouse, ClickhouseSettings
from langchain_community.embeddings.yandex import YandexGPTEmbeddings


def get_db_settings() -> ClickhouseSettings:
    return ClickhouseSettings(
        host='clickhouse',
        database='default',
        table='langchain'
    )


def get_db() -> Clickhouse:
    return Clickhouse(config=get_db_settings(), embedding=get_embeddings())


def get_embeddings() -> YandexGPTEmbeddings:

    FOLDER_ID = os.getenv('FOLDER_ID')
    IAM_TOKEN = os.getenv('IAM_TOKEN')

    return YandexGPTEmbeddings(
        folder_id=FOLDER_ID,
        iam_token=IAM_TOKEN,
    )


def log_tg_message(
        message_id,
        chat_id,
        sender_id,
        sender_name,
        sender_message,
        answer=None,
        context=None,
        rephrased_message=None
):

    db = get_db()

    db.client.command(
        '''CREATE TABLE IF NOT EXISTS default.chat_log (
            timestamp TIMESTAMP DEFAULT now(),
            message_id INT,
            chat_id INT,
            sender_id INT,
            sender_name VARCHAR(50),
            sender_message VARCHAR(4000),
            rephrased_message VARCHAR(4000),
            answer VARCHAR(4000),
            context VARCHAR(),
            reaction VARCHAR(50)
        ) ENGINE = MergeTree()
        ORDER BY timestamp
    ''')


    query = '''
        SELECT COUNT(*), last_value(answer), last_value(context)
        FROM default.chat_log
        WHERE message_id = %(message_id)s
            AND chat_id = %(chat_id)s
        AND sender_id = %(sender_id)s
        AND sender_message = %(sender_message)s;
    '''
    params = {
        'message_id': message_id,
        'chat_id': chat_id,
        'sender_id': sender_id,
        'sender_message': sender_message
    }
    count, _answer, _context = db.client.command(query, params)

    answer = db.escape_str(answer) if answer is not None else None
    answer = _answer if len(_answer) != 0 else answer
    context = db.escape_str(context) if context is not None else None
    context = _context if len(_context) != 0 else context

    if count == '0':
        db.client.command(f'''
            INSERT INTO default.chat_log
                (message_id, chat_id, sender_id, sender_name, sender_message, rephrased_message, answer, context)
            VALUES
                ({message_id}, {chat_id}, {sender_id}, '{sender_name}', '{sender_message}', '{rephrased_message}', '{answer}', '{context}')
        ''')
    else:
        query = '''
            ALTER TABLE default.chat_log
            UPDATE answer = %(answer)s, context = %(context)s
            WHERE message_id = %(message_id)s
            AND chat_id = %(chat_id)s
            AND sender_id = %(sender_id)s
            AND sender_message = %(sender_message)s;
        '''
        params = {
            'answer': answer,
            'context': context,
            'message_id': message_id,
            'chat_id': chat_id,
            'sender_id': sender_id,
            'sender_message': sender_message
        }
        db.client.command(query, params)
