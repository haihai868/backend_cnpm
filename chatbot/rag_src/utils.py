from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_mistralai import MistralAIEmbeddings
from langchain_mistralai import ChatMistralAI

from dotenv import load_dotenv

load_dotenv()

embeddings = MistralAIEmbeddings(
        model="mistral-embed",
    )

llm = ChatMistralAI(
    model="mistral-large-latest",
    temperature=0.7,
)

# # local embeddings model
# embeddings = OllamaEmbeddings(model="nomic-embed-text")

def split_documents(doc: list[Document]) -> list[Document]:
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=80,
        length_function=len,
        is_separator_regex=False
    )

    return text_splitter.split_documents(doc)

def create_product_document(product):
    return Document(
        page_content= 'name:' + product['name']
                      + ' description:' + product['description']
                      + ' age_gender:' + product['age_gender']
                      + ' size:' + product['size']
                      + ' price:' + str(product['price'])
                      + ' quantity_in_stock:' + str(product['quantity_in_stock']),
        metadata={
            'id': product['id'],
            'category_id': product['category_id'],
        },
        id=str(product['id'])
    )
