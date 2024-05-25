from celery import Celery
from celery.schedules import crontab

from libs.broker import app
from libs.workers import (
    download_wiki_qa,
    mirror_wiki,
    embed_path,
    download_wiki_datascheme,
    download_playbooks,
    download_checked_alerts
)

TIME_DUMP = 60*60*24

@app.on_after_configure.connect
def setup_periodic_tasks(sender):
     sender.add_periodic_task(TIME_DUMP, download_wiki_qa, name='download security wiki qa')
     sender.add_periodic_task(TIME_DUMP, download_wiki_datascheme, name='dowload datascheme grid')
     sender.add_periodic_task(TIME_DUMP, mirror_wiki, name='mirror wiki')
     sender.add_periodic_task(TIME_DUMP, embed_path, name='embed corpus directory')
     sender.add_periodic_task(TIME_DUMP, download_playbooks, name='download playbooks')
     sender.add_periodic_task(TIME_DUMP, download_checked_alerts, name='dowload alerts descriptions')


if __name__ == "__main__":
     app.start(['-A', 'libs.workers', 'worker', '-B', '--loglevel=info'])
