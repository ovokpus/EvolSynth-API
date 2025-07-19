"""
OptimizedEvolInstructService - High-Performance LangGraph Implementation
Optimized for speed with async processing, batching, and caching
"""

import asyncio
import aiohttp
import time
import re
from typing import List, Dict, Any, Optional
from concurrent.futures import ThreadPoolExecutor
import redis
import pickle
import hashlib

from langchain_openai import ChatOpenAI
from langchain.schema import Document
from langchain.prompts import ChatPromptTemplate

from api.config import settings
from api.models.core import GenerationSettings, PerformanceMetrics


class EvolInstructService:
    """High-performance version with batching, caching, and async processing"""
    
    def __init__(self):
        """Initialize optimized service with connection pooling and caching"""
        # Connection pool for OpenAI API
        self.llm_pool = self._create_llm_pool()
        
        # Redis cache for results
        self.cache = self._setup_cache()
        
        # Thread pool for CPU-bound tasks
        self.executor = ThreadPoolExecutor(max_workers=settings.max_concurrency)
        
        # Batch settings
        self.batch_size = 5
        self.batch_timeout = 2.0  # seconds
        
    def _create_llm_pool(self):
        """Create connection pool for LLM calls"""
        return [
            ChatOpenAI(
                model=settings.default_model,
                temperature=settings.temperature,
                max_retries=2,
                request_timeout=30
            ) 
            for _ in range(settings.max_concurrency)
        ]
    
    def _setup_cache(self):
        """Setup Redis cache for caching results"""
        try:
            return redis.Redis(
                host='localhost', 
                port=6379, 
                db=0,
                decode_responses=False,
                socket_connect_timeout=5,
                socket_timeout=5
            )
        except:
            print("⚠️  Redis not available, using in-memory cache")
            return {}  # Fallback to dict cache
    
    async def generate_synthetic_data_async(
        self, 
        documents: List[Document], 
        settings: Optional[GenerationSettings] = None
    ) -> Dict[str, Any]:
        """Async version with batched LLM calls and caching"""
        start_time = time.time()
        
        # Check cache first
        cache_key = self._generate_cache_key(documents, settings)
        cached_result = self._get_from_cache(cache_key)
        if cached_result:
            print("🎯 Cache hit! Returning cached result")
            return cached_result
        
        # Process documents in parallel
        base_questions_task = self._generate_base_questions_batch(documents)
        
        # Wait for base questions
        base_questions = await base_questions_task
        
        # Run all evolution types concurrently with batching
        evolution_tasks = [
            self._simple_evolution_batch(base_questions, documents),
            self._multi_context_evolution_batch(base_questions, documents),
            self._reasoning_evolution_batch(base_questions, documents),
            self._complex_evolution_batch(base_questions, documents)
        ]
        
        # Execute all evolution types in parallel
        evolution_results = await asyncio.gather(*evolution_tasks)
        evolved_questions = [q for batch in evolution_results for q in batch]
        
        # Generate answers in batches
        answers_task = self._generate_answers_batch(evolved_questions, documents)
        contexts_task = self._extract_contexts_batch(evolved_questions, documents)
        
        question_answers, question_contexts = await asyncio.gather(
            answers_task, contexts_task
        )
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Create result
        result = {
            "evolved_questions": evolved_questions,
            "question_answers": question_answers,
            "question_contexts": question_contexts,
            "performance_metrics": PerformanceMetrics(
                execution_time_seconds=execution_time,
                questions_generated=len(evolved_questions),
                answers_generated=len(question_answers),
                contexts_extracted=len(question_contexts),
                questions_per_second=len(evolved_questions) / execution_time,
                execution_mode="optimized_async"
            )
        }
        
        # Cache result for future use
        self._save_to_cache(cache_key, result)
        
        return result
    
    def generate_synthetic_data(
        self, 
        documents: List[Document], 
        settings: Optional[GenerationSettings] = None,
        max_iterations: int = 1
    ) -> Dict[str, Any]:
        """Sync wrapper for the async optimized implementation"""
        # Run the async method in a new event loop
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        return loop.run_until_complete(
            self.generate_synthetic_data_async(documents, settings)
        )
    
    async def _generate_base_questions_batch(self, documents: List[Document]) -> List[Dict[str, Any]]:
        """Generate base questions using batched async calls"""
        # Create batches of documents
        doc_batches = [documents[i:i+self.batch_size] for i in range(0, len(documents), self.batch_size)]
        
        # Process batches concurrently
        tasks = [
            self._process_document_batch(batch, "base_questions")
            for batch in doc_batches
        ]
        
        batch_results = await asyncio.gather(*tasks)
        
        # Flatten results
        base_questions = []
        for batch_result in batch_results:
            base_questions.extend(batch_result)
        
        return base_questions
    
    async def _simple_evolution_batch(self, base_questions: List[Dict[str, Any]], documents: List[Document]) -> List[Dict[str, Any]]:
        """Apply simple evolution using batched processing"""
        return await self._evolution_batch(base_questions, documents, "simple_evolution", settings.simple_evolution_count)
    
    async def _multi_context_evolution_batch(self, base_questions: List[Dict[str, Any]], documents: List[Document]) -> List[Dict[str, Any]]:
        """Apply multi-context evolution using batched processing"""
        return await self._evolution_batch(base_questions, documents, "multi_context_evolution", settings.multi_context_evolution_count)
    
    async def _reasoning_evolution_batch(self, base_questions: List[Dict[str, Any]], documents: List[Document]) -> List[Dict[str, Any]]:
        """Apply reasoning evolution using batched processing"""
        return await self._evolution_batch(base_questions, documents, "reasoning_evolution", settings.reasoning_evolution_count)
    
    async def _complex_evolution_batch(self, base_questions: List[Dict[str, Any]], documents: List[Document]) -> List[Dict[str, Any]]:
        """Apply complex meta-cognitive evolution using batched processing"""
        return await self._evolution_batch(base_questions, documents, "complex_evolution", settings.complex_evolution_count)
    
    async def _evolution_batch(self, base_questions: List[Dict[str, Any]], documents: List[Document], evolution_type: str, count: int) -> List[Dict[str, Any]]:
        """Generic batched evolution processing"""
        # Select questions for evolution
        questions_to_evolve = base_questions[:count]
        
        # Create batches
        question_batches = [questions_to_evolve[i:i+self.batch_size] for i in range(0, len(questions_to_evolve), self.batch_size)]
        
        # Process batches concurrently
        tasks = [
            self._process_evolution_batch(batch, documents, evolution_type)
            for batch in question_batches
        ]
        
        batch_results = await asyncio.gather(*tasks)
        
        # Flatten results
        evolved_questions = []
        for batch_result in batch_results:
            evolved_questions.extend(batch_result)
        
        return evolved_questions
    
    async def _process_document_batch(self, doc_batch: List[Document], operation: str) -> List[Dict[str, Any]]:
        """Process a batch of documents asynchronously"""
        loop = asyncio.get_event_loop()
        
        # Run in thread pool to avoid blocking
        return await loop.run_in_executor(
            self.executor,
            self._process_documents_sync,
            doc_batch,
            operation
        )
    
    async def _process_evolution_batch(self, question_batch: List[Dict[str, Any]], documents: List[Document], evolution_type: str) -> List[Dict[str, Any]]:
        """Process a batch of questions for evolution"""
        loop = asyncio.get_event_loop()
        
        return await loop.run_in_executor(
            self.executor,
            self._process_evolution_sync,
            question_batch,
            documents,
            evolution_type
        )
    
    async def _generate_answers_batch(self, questions: List[Dict[str, Any]], documents: List[Document]) -> List[Dict[str, Any]]:
        """Generate answers using batched processing"""
        question_batches = [questions[i:i+self.batch_size] for i in range(0, len(questions), self.batch_size)]
        
        tasks = [
            self._process_answer_batch(batch, documents)
            for batch in question_batches
        ]
        
        batch_results = await asyncio.gather(*tasks)
        
        # Flatten results
        answers = []
        for batch_result in batch_results:
            answers.extend(batch_result)
        
        return answers
    
    async def _extract_contexts_batch(self, questions: List[Dict[str, Any]], documents: List[Document]) -> List[Dict[str, Any]]:
        """Extract contexts using batched processing"""
        loop = asyncio.get_event_loop()
        
        return await loop.run_in_executor(
            self.executor,
            self._extract_contexts_sync,
            questions,
            documents
        )
    
    async def _process_answer_batch(self, question_batch: List[Dict[str, Any]], documents: List[Document]) -> List[Dict[str, Any]]:
        """Process a batch of questions for answer generation"""
        loop = asyncio.get_event_loop()
        
        return await loop.run_in_executor(
            self.executor,
            self._generate_answers_sync,
            question_batch,
            documents
        )
    
    def _process_documents_sync(self, doc_batch: List[Document], operation: str) -> List[Dict[str, Any]]:
        """Synchronous document processing (runs in thread pool)"""
        results = []
        llm = self.llm_pool[0]  # Get LLM from pool
        
        # Base question generation prompt
        base_prompt = ChatPromptTemplate.from_template(
            "Based on the following document, generate 2-3 clear, specific questions that test understanding of the key concepts:\n\n"
            "Document: {document}\n\n"
            "Generate questions that are:\n"
            "- Specific and detailed\n"
            "- Focused on important concepts\n"
            "- Clear and unambiguous\n\n"
            "Questions:"
        )
        
        for doc in doc_batch:
            try:
                # Generate questions using LLM
                response = llm.invoke(base_prompt.format(document=doc.page_content))
                questions_text = response.content
                
                # Parse questions (simple split on question marks)
                questions = [q.strip() + "?" for q in questions_text.split("?") if q.strip()]
                
                for i, question in enumerate(questions[:3]):  # Limit to 3 questions
                    result = {
                        "id": f"base_{id(doc)}_{i}",
                        "question": question,
                        "type": "base_question",
                        "document_id": str(id(doc))
                    }
                    results.append(result)
                    
            except Exception as e:
                print(f"Error generating base questions: {e}")
                # Fallback question
                result = {
                    "id": f"base_{id(doc)}_fallback",
                    "question": "What are the main concepts discussed in this document?",
                    "type": "base_question",
                    "document_id": str(id(doc))
                }
                results.append(result)
        
        return results
    
    def _process_evolution_sync(self, question_batch: List[Dict[str, Any]], documents: List[Document], evolution_type: str) -> List[Dict[str, Any]]:
        """Synchronous evolution processing (runs in thread pool)"""
        results = []
        llm = self.llm_pool[0]  # Get LLM from pool
        
                # Evolution prompts - ultra-clean, direct instructions
        evolution_prompts = {
            "simple_evolution": """
            Make this question more specific and detailed. Return ONLY the improved question, nothing else.

            Original: {question}

            Improved:""",
                        "multi_context_evolution": """
            Rewrite this to require comparing multiple concepts or sources. Return ONLY the new question, nothing else.

            Original: {question}

            New:""",
                        "reasoning_evolution": """
            Make this require logical thinking and analysis steps. Return ONLY the question, nothing else.

            Original: {question}

            Result:""",
                        "complex_evolution": """
            Create an advanced version requiring evaluation and synthesis. Return ONLY the question, nothing else.

            Original: {question}

            Advanced:"""
                    }
        
        prompt_template = ChatPromptTemplate.from_template(evolution_prompts.get(evolution_type, evolution_prompts["simple_evolution"]))
        
        for question in question_batch:
            try:
                original_question = question.get('question', '')
                if not original_question:
                    continue
                    
                # Evolve question using LLM
                response = llm.invoke(prompt_template.format(question=original_question))
                evolved_question = response.content.strip() if hasattr(response, 'content') else str(response).strip()
                
                # Clean up any remaining boilerplate phrases
                evolved_question = self._clean_boilerplate(evolved_question)
                
                evolved_q = {
                    "id": f"evolved_{id(question)}",
                    "question": evolved_question,
                    "evolution_type": evolution_type,
                    "complexity_level": 2 if evolution_type == "simple_evolution" else 3 if evolution_type == "multi_context_evolution" else 4 if evolution_type == "reasoning_evolution" else 5
                }
                results.append(evolved_q)
                
            except Exception as e:
                print(f"Error evolving question: {e}")
                # Fallback to original question
                evolved_q = {
                    "id": f"evolved_{id(question)}",
                    "question": question.get('question', 'What is the main topic of this document?'),
                    "evolution_type": evolution_type,
                    "complexity_level": 2
                }
                results.append(evolved_q)
        
        return results
    
    def _generate_answers_sync(self, question_batch: List[Dict[str, Any]], documents: List[Document]) -> List[Dict[str, Any]]:
        """Synchronous answer generation (runs in thread pool)"""
        results = []
        llm = self.llm_pool[0]  # Get LLM from pool
        
        # Create context from documents
        document_context = "\n\n".join([doc.page_content[:1000] for doc in documents[:3]])
        
        answer_prompt = ChatPromptTemplate.from_template("""
                        Based on the following context, provide a clear and accurate answer to the question:

                        Context:
                        {context}

                        Question: {question}

                        Answer:""")
        
        for question in question_batch:
            try:
                response = llm.invoke(answer_prompt.format(
                    context=document_context,
                    question=question.get('question', '')
                ))
                
                # Clean the response - extract just the answer content
                answer_text = response.content.strip() if hasattr(response, 'content') else str(response).strip()
                
                # Clean up any boilerplate phrases in the answer
                answer_text = self._clean_boilerplate(answer_text)
                
                answer = {
                    "question_id": question["id"],
                    "answer": answer_text
                }
                results.append(answer)
                
            except Exception as e:
                print(f"Error generating answer: {e}")
                # Fallback answer without boilerplate
                answer = {
                    "question_id": question["id"],
                    "answer": "Unable to generate answer based on provided context."
                }
                results.append(answer)
        
        return results
    
    def _clean_boilerplate(self, text: str) -> str:
        """Remove common boilerplate phrases from generated content"""
        # Ultra-aggressive boilerplate removal patterns (most specific first)
        boilerplate_patterns = [
            # Ultra-specific patterns for exact user-reported issues
            r"^a\s+transformed\s+version\s+of\s+the\s+question\s+that\s+requires\s+logical\s+reasoning\s+and\s+multi-step\s+analysis:\s*",
            r"^here'?s?\s+a\s+more\s+specific\s+version\s+of\s+the\s+question:\s*",
            r"^a\s+detailed\s+version\s+of\s+the\s+question\s+that\s+requires\s+synthesis:\s*",
            
            # General boilerplate patterns
            r"^.*?\s+version\s+of\s+the\s+question\s+that\s+.*?:\s*",
            r"^.*?\s+version\s+of\s+the\s+question:\s*",
            r"^.*?\s+that\s+requires?\s+.*?:\s*",
            
            # Evolution type descriptions
            r"^(Simple|Multi-Context|Reasoning|Complex)\s+(Evolution|Question):\s*",
            r"^(Evolved|Improved|Advanced|New|Result):\s*",
            r"^(Question|Answer):\s*",
            
            # Conversational starters
            r"^(Certainly|Sure|Of course|Absolutely|Yes)!?\s*Here'?s?\s+",
            r"^Here'?s?\s+",
            r"^I'll\s+",
            r"^Let me\s+",
            
            # Generated content markers
            r"Generated\s+(answer|question|content)\s+for:\s*",
            r"^Based on.*?:\s*",
            r"^(The\s+)?(following|above)\s+(question|answer|content)\s*",
            
            # Generic descriptions
            r"^This\s+(is\s+)?(a\s+)?question\s+(that|which)\s+",
            r"^(The\s+)?question\s+(is|becomes):\s*",
            
            # Cleanup trailing fragments
            r":\s*$",
            r"that\s*$",
            r"which\s*$",
        ]
        
        cleaned_text = text.strip()
        
        # Apply all boilerplate removal patterns
        for pattern in boilerplate_patterns:
            cleaned_text = re.sub(pattern, "", cleaned_text, flags=re.IGNORECASE | re.MULTILINE)
        
        # Clean up extra whitespace and newlines
        cleaned_text = re.sub(r'\s+', ' ', cleaned_text).strip()
        
        # Remove leading/trailing punctuation artifacts
        cleaned_text = re.sub(r'^[:\-\s]+', '', cleaned_text)
        cleaned_text = re.sub(r'[:\-\s]+$', '', cleaned_text)
        
        # Ensure question ends properly
        if cleaned_text and not cleaned_text.endswith(('?', '.', '!', ':')):
            if any(word in cleaned_text.lower() for word in ['what', 'how', 'why', 'when', 'where', 'which', 'who']):
                cleaned_text += '?'
            else:
                cleaned_text += '.'
        
        return cleaned_text
    
    def _extract_contexts_sync(self, questions: List[Dict[str, Any]], documents: List[Document]) -> List[Dict[str, Any]]:
        """Synchronous context extraction with smart truncation"""
        results = []
        
        for question in questions:
            # Extract contexts with smart truncation at sentence boundaries
            smart_contexts = []
            for doc in documents[:3]:  # Include up to 3 documents instead of 2
                content = doc.page_content
                
                # If content is longer than configured max, find a good break point
                max_length = getattr(settings, 'context_max_length', 1500)
                if len(content) > max_length:
                    # Try to break at sentence boundary within 80%-100% of max length
                    truncated = content[:max_length]
                    last_sentence_end = max(
                        truncated.rfind('.'), 
                        truncated.rfind('!'), 
                        truncated.rfind('?')
                    )
                    
                    min_length = int(max_length * 0.8)  # 80% of max length
                    if last_sentence_end > min_length:  # If we found a good sentence boundary
                        content = content[:last_sentence_end + 1]
                    else:
                        # Fall back to word boundary to avoid cutting mid-word
                        truncated = content[:int(max_length * 0.93)]  # 93% of max length
                        last_space = truncated.rfind(' ')
                        if last_space > min_length:
                            content = content[:last_space] + "..."
                        else:
                            content = truncated + "..."
                
                smart_contexts.append(content)
            
            context = {
                "question_id": question["id"],
                "contexts": smart_contexts
            }
            results.append(context)
        
        return results
    
    def _generate_cache_key(self, documents: List[Document], settings: Optional[GenerationSettings]) -> str:
        """Generate cache key from documents and settings"""
        content_hash = hashlib.md5()
        
        # Hash document content
        for doc in documents:
            content_hash.update(doc.page_content.encode())
        
        # Hash settings
        if settings:
            content_hash.update(str(settings.dict()).encode())
        
        return f"evolsynth:{content_hash.hexdigest()}"
    
    def _get_from_cache(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Get result from cache"""
        try:
            if isinstance(self.cache, dict):
                return self.cache.get(cache_key)
            else:
                cached_data = self.cache.get(cache_key)
                if cached_data:
                    return pickle.loads(cached_data)
        except:
            pass
        return None
    
    def _save_to_cache(self, cache_key: str, result: Dict[str, Any]) -> None:
        """Save result to cache with TTL"""
        try:
            if isinstance(self.cache, dict):
                self.cache[cache_key] = result
            else:
                # Save with 1 hour TTL
                self.cache.setex(cache_key, 3600, pickle.dumps(result))
        except:
            pass 