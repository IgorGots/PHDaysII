from fastapi import FastAPI, Response
from langchain_core.messages import AIMessage

from libs.messages import TgMessage

from libs.llm.brain import soc_brain
from libs.llm.tools import alert_answer, alert_verdict
from libs.llm.evaluate import evaluate

import libs.logger as logger
log = logger.setup_applevel_logger()

app = FastAPI()


@app.post('/v1/tg_alert/')
async def v1_tg_alert(message: TgMessage):
    log.info(message)

    ai_message = AIMessage(content=message.sender_message)

    answer = alert_answer(ai_message)
    return Response(content=answer, media_type="text/plain")


@app.post('/v1/soc_brain/')
async def v1_soc_brain(message: TgMessage):
    answer = soc_brain(message)
    return Response(content=answer, media_type="text/plain")


@app.post('/v1/verdict/')
async def v1_soc_verdict(message: TgMessage):
    answer = alert_verdict(message.sender_message)
    return Response(content=answer, media_type="text/plain")


@app.post('/v1/evaluate/')
async def v1_tg_evaluate(message: TgMessage):
    answer = evaluate(message)
    return Response(content=answer, media_type="text/plain")
