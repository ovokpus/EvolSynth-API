"""
DocumentService - Service for handling document processing and loading
"""

import os
import tempfile
import base64
from typing import List, Dict, Any, Optional, Union
from pathlib import Path

from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyMuPDFLoader, TextLoader

from api.config import settings
from api.models.core import DocumentInput


class DocumentService:
    """Service for processing and loading documents"""
    
    def __init__(self):
        """Initialize the document service"""
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.chunk_size,
            chunk_overlap=settings.chunk_overlap
        )
        
        # Supported file extensions
        self.supported_extensions = {'.pdf', '.txt', '.md'}
    
    def process_document_inputs(
        self, 
        document_inputs: List[DocumentInput]
    ) -> List[Document]:
        """
        Convert DocumentInput objects to LangChain Documents
        
        Args:
            document_inputs: List of DocumentInput objects
            
        Returns:
            List of LangChain Document objects
        """
        documents = []
        
        for doc_input in document_inputs:
            # Create LangChain Document from DocumentInput
            doc = Document(
                page_content=doc_input.content,
                metadata={
                    **doc_input.metadata,
                    "source": doc_input.source or "unknown"
                }
            )
            documents.append(doc)
        
        return documents
    
    def load_documents_from_files(
        self, 
        file_paths: List[str],
        extract_text: bool = True,
        chunk_documents: bool = False
    ) -> List[Document]:
        """
        Load documents from file paths
        
        Args:
            file_paths: List of file paths to load
            extract_text: Whether to extract text from files
            chunk_documents: Whether to chunk the documents
            
        Returns:
            List of LangChain Document objects
        """
        documents = []
        
        for file_path in file_paths:
            try:
                # Load document based on file extension
                if file_path.lower().endswith('.pdf'):
                    docs = self._load_pdf(file_path)
                elif file_path.lower().endswith(('.txt', '.md')):
                    docs = self._load_text_file(file_path)
                else:
                    print(f"Unsupported file type: {file_path}")
                    continue
                
                documents.extend(docs)
                
            except Exception as e:
                print(f"Error loading file {file_path}: {e}")
                continue
        
        # Chunk documents if requested
        if chunk_documents and documents:
            documents = self.text_splitter.split_documents(documents)
        
        return documents
    
    def load_documents_from_base64(
        self,
        base64_files: List[Dict[str, str]],
        chunk_documents: bool = False
    ) -> List[Document]:
        """
        Load documents from base64 encoded files
        
        Args:
            base64_files: List of dicts with 'content' (base64) and 'filename'
            chunk_documents: Whether to chunk the documents
            
        Returns:
            List of LangChain Document objects
        """
        documents = []
        
        for file_data in base64_files:
            try:
                # Decode base64 content
                content = base64.b64decode(file_data['content'])
                filename = file_data.get('filename', 'unknown')
                
                # Write to temporary file
                with tempfile.NamedTemporaryFile(
                    delete=False, 
                    suffix=Path(filename).suffix
                ) as temp_file:
                    temp_file.write(content)
                    temp_path = temp_file.name
                
                # Load document from temporary file
                docs = self.load_documents_from_files([temp_path])
                
                # Update metadata with original filename
                for doc in docs:
                    doc.metadata['source'] = filename
                    doc.metadata['loaded_from'] = 'base64'
                
                documents.extend(docs)
                
                # Clean up temporary file
                os.unlink(temp_path)
                
            except Exception as e:
                print(f"Error processing base64 file {file_data.get('filename', 'unknown')}: {e}")
                continue
        
        # Chunk documents if requested
        if chunk_documents and documents:
            documents = self.text_splitter.split_documents(documents)
        
        return documents
    
    def validate_documents(self, documents: List[Document]) -> Dict[str, Any]:
        """
        Validate a list of documents
        
        Args:
            documents: List of Document objects to validate
            
        Returns:
            Dictionary with validation results
        """
        validation_results = {
            "valid": True,
            "total_documents": len(documents),
            "issues": [],
            "statistics": {}
        }
        
        if not documents:
            validation_results["valid"] = False
            validation_results["issues"].append("No documents provided")
            return validation_results
        
        # Check document content
        empty_docs = 0
        large_docs = 0
        total_chars = 0
        
        for i, doc in enumerate(documents):
            if not doc.page_content or not doc.page_content.strip():
                empty_docs += 1
                validation_results["issues"].append(f"Document {i} has empty content")
            
            content_length = len(doc.page_content)
            total_chars += content_length
            
            # Check if document is too large
            max_size_chars = settings.max_document_size_mb * 1024 * 1024  # Rough estimate
            if content_length > max_size_chars:
                large_docs += 1
                validation_results["issues"].append(f"Document {i} exceeds size limit")
        
        # Update validation status
        if empty_docs > 0 or large_docs > 0:
            validation_results["valid"] = False
        
        # Add statistics
        validation_results["statistics"] = {
            "empty_documents": empty_docs,
            "oversized_documents": large_docs,
            "total_characters": total_chars,
            "average_characters": total_chars / len(documents) if documents else 0,
            "valid_documents": len(documents) - empty_docs - large_docs
        }
        
        return validation_results
    
    def create_sample_documents(self) -> List[Document]:
        """
        Create sample documents for demonstration purposes
        
        Returns:
            List of sample Document objects
        """
        sample_documents = [
            Document(
                page_content="Federal student loan programs provide funding for undergraduate and graduate students pursuing higher education. These programs include Direct Subsidized Loans, Direct Unsubsidized Loans, and Direct PLUS Loans. Eligibility requirements vary by program and include enrollment in an eligible degree program, satisfactory academic progress, and completion of the FAFSA application.",
                metadata={"source": "sample_federal_loans.txt", "type": "sample"}
            ),
            Document(
                page_content="The Pell Grant is a federal financial aid program that provides need-based grants to undergraduate students. Unlike loans, Pell Grants do not need to be repaid. The amount of the grant depends on financial need, cost of attendance, enrollment status, and length of the academic program. Students must maintain satisfactory academic progress to continue receiving Pell Grant funding.",
                metadata={"source": "sample_pell_grants.txt", "type": "sample"}
            ),
            Document(
                page_content="Academic calendars determine the timing and structure of financial aid disbursements throughout the academic year. Students enrolled in traditional semester or quarter systems receive aid disbursements at the beginning of each term. For students in non-traditional or accelerated programs, disbursement schedules may vary based on the specific academic calendar and program requirements.",
                metadata={"source": "sample_academic_calendar.txt", "type": "sample"}
            )
        ]
        
        return sample_documents
    
    def _load_pdf(self, file_path: str) -> List[Document]:
        """Load PDF document using PyMuPDFLoader"""
        loader = PyMuPDFLoader(file_path)
        return loader.load()
    
    def _load_text_file(self, file_path: str) -> List[Document]:
        """Load text file using TextLoader"""
        loader = TextLoader(file_path, encoding='utf-8')
        return loader.load()
    
    def get_document_summary(self, documents: List[Document]) -> Dict[str, Any]:
        """
        Generate a summary of the loaded documents
        
        Args:
            documents: List of Document objects
            
        Returns:
            Dictionary with document summary information
        """
        if not documents:
            return {"total_documents": 0, "total_characters": 0, "sources": []}
        
        total_chars = sum(len(doc.page_content) for doc in documents)
        sources = list(set(doc.metadata.get("source", "unknown") for doc in documents))
        
        # Count pages if available
        total_pages = 0
        for doc in documents:
            if "page" in doc.metadata:
                total_pages += 1
        
        return {
            "total_documents": len(documents),
            "total_characters": total_chars,
            "average_characters": total_chars / len(documents),
            "total_pages": total_pages if total_pages > 0 else None,
            "sources": sources,
            "unique_sources": len(sources)
        } 