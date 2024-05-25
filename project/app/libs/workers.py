import os
import shutil

from celery import chain

from libs.broker import app
from libs.splitters import splitter_md, splitter_csv
from libs.my_company import soar, wiki
from libs import text
from libs.db import get_db, get_db_settings, get_embeddings


TOKEN_GITLAB = os.getenv('TOKEN_GITLAB')
DIR_CACHE = os.getenv('DIR_CACHE')
DIR_NLTK = os.getenv('DIR_NLTK')


@app.task()
def text_sanitize(filename: str) -> str:
    """Clean file

    Args:
        filename (str): source file

    Returns:
        str: cleaned file
    """
    with open(filename, 'r') as source_file:
        source_text = source_file.read()

    cleaned_text = text.clean_text(source_text)

    with open(filename, 'w') as destination_file:
        destination_file.write(cleaned_text)

    return filename


@app.task(max_concurrency=1)
def file_embed(filename: str, dist: float = 0.1) -> str:
    """Check file for embedding

    Args:
        filename (str): filename
        dist (float, optional): similarity distantion. Defaults to 0.1.

    Returns:
        str: file name
    """
    vectorstore = get_db()
    embedding = get_embeddings()

    _, extension = os.path.splitext(filename)
    if extension in ['.yaml', '.yml']:
        docs = splitter_md(filename)
    elif extension in ['.md']:
        docs = splitter_md(filename)
    elif extension in ['.csv']:
        docs = splitter_csv(filename)
    else:
        docs = splitter_md(filename)

    _docs = docs.copy()

    # check that doc exists in database or there are similar docs
    for d in _docs:
        pass

    split = 100
    for i in range(0, len(docs), split):
        vectorstore.from_documents(
            documents=docs[i:i+split],
            embedding=embedding,
            config=get_db_settings()
        )

    return filename


@app.task
def file_remove(filename: str) -> None:
    os.remove(filename)


@app.task
def dir_remove(dir: str) -> None:
    shutil.rmtree(dir)


@app.task
def download_wiki_qa() -> None:
    wk = wiki.Wiki()
    qa_list = wk.grid_to_dict('security/what-is-this')
    for qa in qa_list:
        filename = text.string_to_path(
            f'''{qa['Что это'].strip().replace(' ', '_').replace('/', '_')}.md'''
        ) + '.md'
        filename = os.path.join(DIR_CACHE, filename)
        with open(filename, 'w') as f:
            f.write(f'''Question: Что такое {qa['Что это']}?\n''')
            f.write(f'''Answer: {qa['значит']}\n''')

        chain(text_sanitize.s(filename), file_embed.s(), file_remove.s())()


@app.task
def download_wiki_datascheme() -> None:
    wk = wiki.Wiki()
    grid = wk.grid_to_dict('/soc/datascheme')
    for row in grid:
        if len(row['index']) > 0 and len(row['sourcetype']) > 0:
            filename = text.string_to_path(
                f'''{row['index']}_{row['sourcetype']}_{row['st'].split('/')[-1]}'''
            ) + '.md'
            filename = os.path.join(DIR_CACHE, filename)
            with open(filename, 'w') as f:
                f.write(f'''\
#Информация о журнале\\логе

## index
{row['index']}
## sourcetype
{row['sourcetype']}
## ticket
{row['st']}
## description
{row['description']}
## Как искать:
```
index={row['index']} sourcetype={row['sourcetype']}
```
''')

            chain(text_sanitize.s(filename), file_embed.s(), file_remove.s())()


# pagets for crawlers
start_pages = [
    'https://wiki.mycompany.ru/security',
    'https://wiki.mycompany.ru/security/soc',
    'https://wiki.mycompany.ru/product-security/'
]


@app.task(max_concurrency=1)
def mirror_wiki(pages=start_pages):
    wk = wiki.Wiki()
    urls = wiki.get_wiki_urls(wk, pages, depth=2)
    for url in urls:
        filename = wiki.download_wiki_page(wk, DIR_CACHE, url)
        chain(text_sanitize.s(filename), file_embed.s(), file_remove.s())()


@app.task(max_concurrency=1)
def embed_path(path='/corpus', filter_filename=[], filter_path=[]):
    """Embed predefined data from corpus directory

    Args:
        path (str, optional): corpus path_. Defaults to '/corpus'.
        filter_filename (list, optional): filter list. Defaults to [].
        filter_path (list, optional): filter path. Defaults to [].
    """
    for root, _, filenames in os.walk(path):
        for _filename in filenames:
            print(_filename)
            if _filename not in filter_filename and root not in filter_path:
                filename = os.path.join(root, _filename)
                chain(text_sanitize.s(filename), file_embed.s())()


@app.task(max_concurrency=1)
def download_playbooks():
    """Download alerts descriptions
    """

    playbooks = soar.get_playbooks()
    for playbook in playbooks:
        chain(text_sanitize.s(playbook), file_embed.s(), file_remove.s())()


@app.task(max_concurency=1)
def download_checked_alerts():
    """
    Download checked alerts
    """

    alerts = soar.get_checked_alerts()

    for alert in alerts:
        chain(text_sanitize.s(alert), file_embed.s(), file_remove.s())()
