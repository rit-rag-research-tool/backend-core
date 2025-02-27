import chromadb
from typing import Any, List, Optional, Dict


class CromaDBClient:
    def __init__(self, env: Dict[str, Any]):

        if env["CROMA_API_URL"].contains(":"):
            host, port = env["CROMA_API_URL"].split(":")
            self.client = chromadb.HttpClient(
                ssl=True,
                host=host,
                port=port,
                tenant=env["CROMA_TENANT"],
                database=env["CROMA_DATABASE"],
                headers={
                    "x-chroma-token": env["CROMA_TOKEN"]
                }
            )
        else: 
            self.client = chromadb.HttpClient(
                ssl=True,
                host=env["CROMA_API_URL"],
                tenant=env["CROMA_TENANT"],
                database=env["CROMA_DATABASE"],
                headers={
                    "x-chroma-token": env["CROMA_TOKEN"]
                }
            )
  
    def create_collection(self, name: str) -> bool:
        try:
            self.client.create_collection(name=name)
            return True
        except Exception as e:
            print(f"Error creating collection: {str(e)}")
            return False

    def get_collection(self, name: str) -> Optional[Any]:
        try:
            return self.client.get_collection(name=name)
        except Exception as e:
            print(f"Error retrieving collection: {str(e)}")
            return None

    def add_document(self, collection_name: str, uri: str, embeddings: List[float], hash: str) -> bool:
        try:
            collection = self.client.get_collection(name=collection_name)
            collection.add(ids=[hash], uris=[uri], embeddings=embeddings, metadatas=[{}])
            return True
        except Exception as e:
            print(f"Error adding document to collection {collection_name}: {str(e)}")
            return False

    def get_document(self, collection_name: str, document_id: str) -> Optional[str]:
        try:
            collection = self.client.get_collection(name=collection_name)
            result = collection.get(ids=[document_id])
            if result and isinstance(result, dict) and 'documents' in result and result['documents']:
                return result['documents'][0]
            return None
        except Exception as e:
            print(f"Error retrieving document {document_id} from collection {collection_name}: {str(e)}")
            return None

    def delete_document(self, collection_name: str, document_id: str) -> bool:
        try:
            collection = self.client.get_collection(name=collection_name)
            collection.delete(ids=[document_id])
            return True
        except Exception as e:
            print(f"Error deleting document {document_id} from collection {collection_name}: {str(e)}")
            return False

    def list_collections(self) -> List[str]:
        try:
            return [col.name for col in self.client.list_collections()]
        except Exception as e:
            print(f"Error listing collections: {str(e)}")
            return []

    def delete_collection(self, name: str) -> bool:
        try:
            self.client.delete_collection(name=name)
            return True
        except Exception as e:
            print(f"Error deleting collection {name}: {str(e)}")
            return False

    def close_connection(self) -> None:
        # ChromaDB HttpClient doesn't require explicit connection closing
        pass

    def update_metadata(self, collection_name: str, document_id: str, metadata: Dict[str, Any]) -> bool:
        try:
            collection = self.client.get_collection(name=collection_name)
            collection.update(ids=[document_id], metadatas=[metadata])
            return True
        except Exception as e:
            print(f"Error updating metadata for document {document_id} in collection {collection_name}: {str(e)}")
            return False
        
    def get_metadata(self, collection_name: str, document_id: str) -> Optional[Dict[str, Any]]:
        try:
            collection = self.client.get_collection(name=collection_name)
            result = collection.get(ids=[document_id])
            if result and isinstance(result, dict) and 'metadatas' in result and result['metadatas']:
                return dict(result['metadatas'][0])
            return None
        except Exception as e:
            print(f"Error retrieving metadata for document {document_id} from collection {collection_name}: {str(e)}")
            return None