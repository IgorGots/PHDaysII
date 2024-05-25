from langchain_community.document_loaders import CSVLoader, UnstructuredMarkdownLoader, DirectoryLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter, MarkdownHeaderTextSplitter

import libs.logger as logger
logging = logger.setup_applevel_logger()


def splitter_md(filename: str, split: bool = True, chunk_size=3000, chunk_overlap=100):

    # loader = UnstructuredMarkdownLoader(filename, mode="single", strategy="fast")
    loader = TextLoader(filename)
    docs = loader.load()

    if split:
        # md_splitter = MarkdownHeaderTextSplitter(strip_headers=False, headers_to_split_on=[("#", "Header 1")])
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)

        # docs = text_splitter.split_documents(
        #     md_splitter.split_text(docs)
        # )
        docs = text_splitter.split_documents(docs)

    return docs


def splitter_csv(filename: str, split: bool = True, chunk_size=3000, chunk_overlap=100):

    loader = CSVLoader(filename)
    return loader.load()


# def splitter_txt(data_dir: str, glob='**/*.txt', split=True):

#     loader = DirectoryLoader(data_dir, glob=glob, loader_cls=TextLoader)
#     docs = loader.load()

#     if split:
#         text_splitter = RecursiveCharacterTextSplitter(chunk_size=3000, chunk_overlap=100)
#         return text_splitter.split_documents(docs)
#     else:
#         return docs


# def splitter_yml(data_dir: str, glob='**/*.yaml', split=True):

#     loader = DirectoryLoader(data_dir, glob=glob, loader_cls=TextLoader)
#     docs = loader.load()

#     if split:
#         text_splitter = RecursiveCharacterTextSplitter(chunk_size=3000, chunk_overlap=100)
#         return text_splitter.split_documents(docs)
#     else:
#         return docs
