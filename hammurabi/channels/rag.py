from langchain.retrievers import EnsembleRetriever
from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from langchain_openai import ChatOpenAI
from langchain.retrievers.self_query.base import SelfQueryRetriever
from langchain.chains.query_constructor.base import AttributeInfo
from langchain_elasticsearch import ElasticsearchStore
from langchain.retrievers.multi_query import MultiQueryRetriever
from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import LLMChainExtractor
import dotenv
import os                                                                                                                                                                                                          

  
class Rag():

    dotenv.load_dotenv()

    def get_pinecone_vectorstore(self):
        embeddings = OpenAIEmbeddings(model='text-embedding-3-large')# aryan recommened
        vectorstore = PineconeVectorStore(  embedding=embeddings,
                                            index_name="hukukai",
                                            )

        return vectorstore

    def get_retriver(self, retrivers):
        ensemble_retriever = EnsembleRetriever(retrievers=retrivers)
        return ensemble_retriever


    def self_querying_retriever(self, vectorstore):
        llm = ChatOpenAI(        temperature=0,
        max_tokens=800,
        model_kwargs={"top_p": 0, "frequency_penalty": 0, "presence_penalty": 0},
        model='gpt-3.5-turbo')
        metadata_field_info = [AttributeInfo(name= 'source', description= 'kaynak belge', type='string',), AttributeInfo(name='source_type', description= 'metin dili', type='string',),
                        AttributeInfo(name='text', description= 'metnin kendisi', type='string',), AttributeInfo(name='esas', description= 'esas numarasi', type='string',),
                        AttributeInfo(name='karar', description= 'karar numarasi', type='string',)]
        document_content_description = "ictihat metinleri"
        retriever = SelfQueryRetriever.from_llm(
        llm= llm,
        vectorstore= vectorstore,
        metadata_field_info=metadata_field_info,
        document_contents= document_content_description
            )   
        return retriever

    def multi_query_retriever(self, retriever):
        llm = ChatOpenAI(
        temperature=0,
        max_tokens=800,
        model_kwargs={"top_p": 0, "frequency_penalty": 0, "presence_penalty": 0},
        model='gpt-3.5-turbo'
    )


        retriever = MultiQueryRetriever.from_llm(
            retriever=retriever, llm=llm
            )
        
        return retriever
    
    def add_documents_pinecone(self,chunks):
        self.pinecone_vs.add_documents(chunks)

    def get_es_vectorstore(self):
        embeddings= OpenAIEmbeddings(model='text-embedding-3-large')
        db = ElasticsearchStore(es_cloud_id=os.getenv('elasticsearch_cloud_id'),
        index_name=os.getenv('PC_INDEX'),
        es_api_key= os.getenv('es_api_key'),
        embedding=embeddings)
    
        return db
    def get_relevant_documents(self, documents):
        sources = []
        for document in documents:
            sources.append(document.metadata['source'])
        
        return(sources)

    def contextual_compression(self, query, retriever):

        llm= ChatOpenAI(temperature=0,
        max_tokens=800,
        model_kwargs={"top_p": 0, "frequency_penalty": 0, "presence_penalty": 0},
        model='gpt-3.5-turbo')
        compressor = LLMChainExtractor.from_llm(llm)
        compression_retriever = ContextualCompressionRetriever(
            base_compressor=compressor, base_retriever=retriever
        )

        compressed_docs = compression_retriever.invoke(query)
        return(compressed_docs)


    def rag_context(self, query):
        pinecone_vs = self.get_pinecone_vectorstore()
        self_querying = self.self_querying_retriever(pinecone_vs)
        ensemble_retriever = self.get_retriver(retrivers=[pinecone_vs.as_retriever(), self_querying])
        retriever = self.multi_query_retriever(retriever=ensemble_retriever)
        documents= retriever.invoke(input=query)
        print(self.get_relevant_documents(documents))
        comp_doc = self.contextual_compression(query=query,retriever=pinecone_vs.as_retriever())
    
        return documents