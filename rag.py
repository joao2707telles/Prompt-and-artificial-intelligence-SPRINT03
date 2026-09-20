
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_google_genai import GoogleGenerativeAIEmbeddings


PDF_PATH = "GW_HCA-G2_Datasheet-PT.pdf"


def criar_vector_store():

    loader = PyPDFLoader(PDF_PATH)
    documentos = loader.load()

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )

    chunks = splitter.split_documents(documentos)

    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/gemini-embedding-001"
    )

    vector_store = InMemoryVectorStore(
        embeddings
    )

    vector_store.add_documents(chunks)

    return vector_store


VECTOR_STORE = criar_vector_store()


def buscar_contexto(pergunta, k=3):

    resultados = VECTOR_STORE.similarity_search(
        pergunta,
        k=k
    )

    contexto = "\n\n".join(
        documento.page_content
        for documento in resultados
    )

    return contexto
