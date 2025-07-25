"""
OptimizedEvolInstructService - High-Performance LangGraph Implementation
Optimized for speed with async processing, batching, and caching
"""

import asyncio
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
        self.executor = ThreadPoolExecutor(
            max_workers=settings.max_concurrency)

        # Optimized batch settings from config
        self.batch_size = getattr(settings, 'batch_size', 8)
        self.batch_timeout = 1.5  # Reduced timeout for faster processing

    def _create_llm_pool(self):
        """Create optimized connection pool for LLM calls"""
        return [
            ChatOpenAI(
                model=settings.default_model,
                temperature=settings.temperature,
                max_retries=2,
                timeout=getattr(settings, 'llm_request_timeout', 30)
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
        answers_task = self._generate_answers_batch(
            evolved_questions, documents)
        contexts_task = self._extract_contexts_batch(
            evolved_questions, documents)

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
        # Check if we're already in an async context
        try:
            asyncio.get_running_loop()
            # We're in an async context, need to use thread executor
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(
                    asyncio.run,
                    self.generate_synthetic_data_async(documents, settings)
                )
                return future.result()
        except RuntimeError:
            # No running loop, create a new one
            return asyncio.run(
                self.generate_synthetic_data_async(documents, settings)
            )

    async def generate_synthetic_data_fast(
        self,
        documents: List[Document],
        settings: Optional[GenerationSettings] = None
    ) -> Dict[str, Any]:
        """ULTRA-FAST version: Single API call for all question generation"""
        start_time = time.time()

        # Check cache first
        cache_key = self._generate_cache_key(documents, settings) + "_fast"
        cached_result = self._get_from_cache(cache_key)
        if cached_result:
            print("🎯 Cache hit! Returning cached result")
            return cached_result

        # Combine all documents into a single context
        combined_content = "\n\n".join([
            f"Document {i+1} ({doc.metadata.get('source', 'Unknown')}): {doc.page_content[:1500]}"
            for i, doc in enumerate(documents[:3])  # Limit to 3 docs for speed
        ])

        # Single comprehensive prompt for questions and answers ONLY
        comprehensive_prompt = ChatPromptTemplate.from_template("""
        Based on the following documents, generate a comprehensive set of questions and answers for evaluation purposes.

        Documents:
        {documents}

        Generate exactly {simple_count} simple questions, {multi_context_count} multi-context questions, and {reasoning_count} reasoning questions.

        For each question, provide:
        1. The question text
        2. A clear, accurate answer

        Format your response as a structured list:

        SIMPLE QUESTIONS:
        Q1: [Question]
        A1: [Answer]

        Q2: [Question]
        A2: [Answer]

        MULTI-CONTEXT QUESTIONS:
        Q3: [Question requiring multiple sources]
        A3: [Answer]

        REASONING QUESTIONS:
        Q4: [Question requiring analysis]
        A4: [Answer]

        Keep answers concise but accurate. Focus on generating high-quality questions and answers.
        """)

        try:
            # Single LLM call for questions and answers ONLY
            llm = self.llm_pool[0]
            response = llm.invoke(comprehensive_prompt.format(
                documents=combined_content,
                simple_count=getattr(settings, 'simple_evolution_count', 2),
                multi_context_count=getattr(settings, 'multi_context_evolution_count', 1),
                reasoning_count=getattr(settings, 'reasoning_evolution_count', 1),
                source="{source}"  # Placeholder for dynamic source
            ))

            response_text = str(response.content) if hasattr(response, 'content') else str(response)
            
            # Parse questions and answers from LLM response
            evolved_questions, question_answers, _ = self._parse_comprehensive_response(
                response_text, documents
            )
            
            # Use FAST keyword-based context extraction with AI summaries
            question_contexts = self._extract_contexts_fast(evolved_questions, documents)

        except Exception as e:
            print(f"Error in fast generation: {e}")
            # Fallback to minimal results
            evolved_questions = [{"id": "fallback_1", "question": "What are the main topics in these documents?", "evolution_type": "simple_evolution", "complexity_level": 2}]
            question_answers = [{"question_id": "fallback_1", "answer": "The documents discuss various topics that require further analysis."}]
            # Use fast context extraction even for fallback
            question_contexts = self._extract_contexts_fast(evolved_questions, documents)

        end_time = time.time()
        execution_time = end_time - start_time

        result = {
            "evolved_questions": evolved_questions,
            "question_answers": question_answers,
            "question_contexts": question_contexts,
            "performance_metrics": PerformanceMetrics(
                execution_time_seconds=execution_time,
                questions_generated=len(evolved_questions),
                answers_generated=len(question_answers),
                contexts_extracted=len(question_contexts),
                questions_per_second=len(evolved_questions) / execution_time if execution_time > 0 else 0,
                execution_mode="ultra_fast_single_call"
            )
        }

        # Cache result
        self._save_to_cache(cache_key, result)
        return result

    async def _generate_base_questions_batch(self, documents: List[Document]) -> List[Dict[str, Any]]:
        """Generate base questions using batched async calls"""
        # Create batches of documents
        doc_batches = [documents[i:i+self.batch_size]
                       for i in range(0, len(documents), self.batch_size)]

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
        count = min(len(base_questions),
                    settings.simple_evolution_count)  # Don't exceed available questions
        return await self._evolution_batch(base_questions[:count], documents, "simple_evolution", count)

    async def _multi_context_evolution_batch(self, base_questions: List[Dict[str, Any]], documents: List[Document]) -> List[Dict[str, Any]]:
        """Apply multi-context evolution using batched processing"""
        count = min(len(base_questions),
                    settings.multi_context_evolution_count)
        return await self._evolution_batch(base_questions[:count], documents, "multi_context_evolution", count)

    async def _reasoning_evolution_batch(self, base_questions: List[Dict[str, Any]], documents: List[Document]) -> List[Dict[str, Any]]:
        """Apply reasoning evolution using batched processing"""
        count = min(len(base_questions), settings.reasoning_evolution_count)
        return await self._evolution_batch(base_questions[:count], documents, "reasoning_evolution", count)

    async def _complex_evolution_batch(self, base_questions: List[Dict[str, Any]], documents: List[Document]) -> List[Dict[str, Any]]:
        """Apply complex meta-cognitive evolution using batched processing"""
        count = min(len(base_questions), settings.complex_evolution_count)
        return await self._evolution_batch(base_questions[:count], documents, "complex_evolution", count)

    async def _evolution_batch(self, base_questions: List[Dict[str, Any]], documents: List[Document], evolution_type: str, count: int) -> List[Dict[str, Any]]:
        """Generic batched evolution processing"""
        # Select questions for evolution
        questions_to_evolve = base_questions[:count]

        # Create batches
        question_batches = [questions_to_evolve[i:i+self.batch_size]
                            for i in range(0, len(questions_to_evolve), self.batch_size)]

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
        loop = asyncio.get_running_loop()

        # Run in thread pool to avoid blocking
        return await loop.run_in_executor(
            self.executor,
            self._process_documents_sync,
            doc_batch,
            operation
        )

    async def _process_evolution_batch(self, question_batch: List[Dict[str, Any]], documents: List[Document], evolution_type: str) -> List[Dict[str, Any]]:
        """Process a batch of questions for evolution"""
        loop = asyncio.get_running_loop()

        return await loop.run_in_executor(
            self.executor,
            self._process_evolution_sync,
            question_batch,
            documents,
            evolution_type
        )

    async def _generate_answers_batch(self, questions: List[Dict[str, Any]], documents: List[Document]) -> List[Dict[str, Any]]:
        """Generate answers using batched processing"""
        question_batches = [questions[i:i+self.batch_size]
                            for i in range(0, len(questions), self.batch_size)]

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
        loop = asyncio.get_running_loop()

        return await loop.run_in_executor(
            self.executor,
            self._extract_contexts_sync,
            questions,
            documents
        )

    async def _process_answer_batch(self, question_batch: List[Dict[str, Any]], documents: List[Document]) -> List[Dict[str, Any]]:
        """Process a batch of questions for answer generation"""
        loop = asyncio.get_running_loop()

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
                response = llm.invoke(
                    base_prompt.format(document=doc.page_content))
                questions_text = str(response.content) if hasattr(response, 'content') else str(response)

                # Parse questions (simple split on question marks)
                questions = [
                    q.strip() + "?" for q in questions_text.split("?") if q.strip()]

                # Limit to 3 questions
                for i, question in enumerate(questions[:3]):
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

        prompt_template = ChatPromptTemplate.from_template(
            evolution_prompts.get(evolution_type, evolution_prompts["simple_evolution"]))

        for question in question_batch:
            try:
                original_question = question.get('question', '')
                if not original_question:
                    continue

                # Evolve question using LLM
                response = llm.invoke(
                    prompt_template.format(question=original_question))
                evolved_question = str(response.content).strip() if hasattr(
                    response, 'content') else str(response).strip()

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

        # Create optimized context from documents (reduced processing)
        document_context = "\n\n".join(
            [doc.page_content[:800] for doc in documents[:2]])

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
                answer_text = str(response.content).strip() if hasattr(
                    response, 'content') else str(response).strip()

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
            cleaned_text = re.sub(pattern, "", cleaned_text,
                                  flags=re.IGNORECASE | re.MULTILINE)

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
        """Question-specific context extraction with relevance-based selection and source tracking"""
        results = []
        llm = self.llm_pool[0]  # Get LLM from pool

        # Create question-specific context extraction prompt
        context_extraction_prompt = ChatPromptTemplate.from_template("""
        Given this specific question and document content, extract and summarize ONLY the information that is directly relevant to answering this question. Focus on the specific concepts, facts, or details that would help answer the question.

        Question: {question}

        Document Content: {content}

        Instructions:
        - Extract only information relevant to the specific question
        - Summarize in 2-3 sentences
        - If the document doesn't contain relevant information, say "No relevant information found in this section"
        - Focus on specific details that help answer the question

        Relevant Context:""")

        for question in questions:
            question_text = question.get('question', '')
            question_specific_contexts = []

            # Process each document to find question-relevant content
            for doc_index, doc in enumerate(documents[:3]):  # Check up to 3 documents for better coverage
                content = doc.page_content
                # Get proper document title (same as fast method)
                doc_source = self._get_document_title(doc, doc_index)
                
                extracted_context_text = None

                # For short content, check relevance before including
                if len(content) <= 400:
                    # Quick relevance check for short content
                    if self._is_content_relevant(question_text, content):
                        extracted_context_text = content
                else:
                    try:
                        # Use LLM to extract question-specific context
                        response = llm.invoke(context_extraction_prompt.format(
                            question=question_text,
                            # Use more content for better context
                            content=content[:2000]
                        ))
                        extracted_context = str(response.content).strip() if hasattr(
                            response, 'content') else str(response).strip()

                        # Clean up any boilerplate from the response
                        extracted_context = self._clean_boilerplate(
                            extracted_context)

                        # Only include if relevant information was found
                        if extracted_context and not any(phrase in extracted_context.lower() for phrase in [
                            "no relevant information", "not relevant", "doesn't contain", "does not contain"
                        ]):
                            extracted_context_text = extracted_context

                    except Exception as e:
                        print(
                            f"Error extracting question-specific context: {e}")
                        # Fallback: try simple keyword matching
                        if self._is_content_relevant(question_text, content):
                            truncated = content[:600]
                            last_period = truncated.rfind('.')
                            if last_period > 400:
                                extracted_context_text = content[:last_period + 1]
                            else:
                                extracted_context_text = truncated + "..."

                # If we found relevant context, create AI summary
                if extracted_context_text:
                    ai_summary = self._create_ai_summary(extracted_context_text, question_text, doc_source)
                    context_with_source = {
                        "text": ai_summary,
                        "source": doc_source,
                        "document_index": doc_index
                    }
                    question_specific_contexts.append(context_with_source)

            # If no specific contexts found, provide AI summary fallback
            if not question_specific_contexts:
                # Create AI summary from the first document
                first_doc = documents[0] if documents else None
                if first_doc:
                    doc_title = self._get_document_title(first_doc, 0)
                    fallback_content = first_doc.page_content[:800]
                    ai_summary = self._create_ai_summary(fallback_content, question_text, doc_title)
                    question_specific_contexts.append({
                        "text": ai_summary,
                        "source": doc_title,
                        "document_index": 0
                    })
                else:
                    question_specific_contexts.append({
                        "text": "No document content available",
                        "source": "Unknown",
                        "document_index": 0
                    })

            context = {
                "question_id": question["id"],
                # Return only the SINGLE most relevant context
                "contexts": question_specific_contexts[:1]  # Only 1 context now
            }
            results.append(context)

        return results

    def _extract_contexts_fast(self, questions: List[Dict[str, Any]], documents: List[Document]) -> List[Dict[str, Any]]:
        """ULTRA-FAST context extraction with AI summarization and proper document titles - SINGLE BEST CONTEXT"""
        results = []
        
        for question in questions:
            question_text = question.get('question', '')
            
            # Find the MOST relevant document instead of all relevant ones
            best_doc = None
            best_score = 0
            best_doc_index = 0
            
            # Score each document for relevance
            for doc_index, doc in enumerate(documents[:3]):  # Limit to 3 docs for speed
                content = doc.page_content
                
                # Calculate relevance score (more sophisticated than just boolean)
                score = self._calculate_relevance_score(question_text, content)
                
                if score > best_score:
                    best_score = score
                    best_doc = doc
                    best_doc_index = doc_index
            
            # Create AI summary for the MOST relevant document only
            if best_doc and best_score > 0:
                doc_source = self._get_document_title(best_doc, best_doc_index)
                context_snippet = self._extract_relevant_snippet(question_text, best_doc.page_content)
                ai_summary = self._create_ai_summary(context_snippet, question_text, doc_source)
                
                question_specific_contexts = [{
                    "text": ai_summary,
                    "source": doc_source,
                    "document_index": best_doc_index
                }]
            else:
                # Fallback to first document if no relevant content found
                first_doc = documents[0] if documents else None
                if first_doc:
                    doc_title = self._get_document_title(first_doc, 0)
                    fallback_content = first_doc.page_content[:800]
                    ai_summary = self._create_ai_summary(fallback_content, question_text, doc_title)
                    
                    question_specific_contexts = [{
                        "text": ai_summary,
                        "source": doc_title,
                        "document_index": 0
                    }]
                else:
                    question_specific_contexts = [{
                        "text": "No documents available for context extraction. Please upload documents to generate relevant context.",
                        "source": "System Message",
                        "document_index": -1
                    }]
            
            results.append({
                "question_id": question["id"],
                "contexts": question_specific_contexts  # Always exactly 1 context now
            })
        
        return results

    def _extract_relevant_snippet(self, question: str, content: str, max_length: int = 300) -> str:
        """Extract relevant snippet from content using keyword matching"""
        # Get key terms from question
        common_words = {'what', 'how', 'why', 'when', 'where', 'who', 'which', 'is', 'are',
                        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
        question_words = set(word.lower().strip('?.,!') for word in question.split())
        key_terms = list(question_words - common_words)
        
        if not key_terms:
            # No specific terms, return beginning of content
            return content[:max_length] + ("..." if len(content) > max_length else "")
        
        # Find best matching sentences
        sentences = content.split('.')
        scored_sentences = []
        
        for i, sentence in enumerate(sentences[:20]):  # Check first 20 sentences only for speed
            sentence_lower = sentence.lower()
            score = sum(1 for term in key_terms if term in sentence_lower)
            if score > 0:
                scored_sentences.append((score, i, sentence.strip()))
        
        if scored_sentences:
            # Sort by score and take top sentences
            scored_sentences.sort(key=lambda x: x[0], reverse=True)
            best_sentences = [sent[2] for sent in scored_sentences[:3]]  # Top 3 sentences
            result = '. '.join(best_sentences)
            
            if len(result) > max_length:
                result = result[:max_length] + "..."
            
            return result
        else:
            # Fallback: find paragraph containing key terms
            paragraphs = content.split('\n\n')
            for paragraph in paragraphs[:10]:  # Check first 10 paragraphs
                paragraph_lower = paragraph.lower()
                if any(term in paragraph_lower for term in key_terms):
                    if len(paragraph) > max_length:
                        return paragraph[:max_length] + "..."
                    return paragraph
            
            # Final fallback
            return content[:max_length] + ("..." if len(content) > max_length else "")

    def _is_content_relevant(self, question: str, content: str) -> bool:
        """Simple keyword-based relevance check"""
        if not question or not content:
            return False

        # Extract key terms from question (remove common words)
        common_words = {'what', 'how', 'why', 'when', 'where', 'who', 'which', 'is', 'are',
                        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
        question_words = set(word.lower().strip('?.,!')
                             for word in question.split())
        key_terms = question_words - common_words

        # Check if any key terms appear in content
        content_lower = content.lower()
        return any(term in content_lower for term in key_terms if len(term) > 2)

    def _calculate_relevance_score(self, question: str, content: str) -> float:
        """Calculate numeric relevance score for better document ranking"""
        if not question or not content:
            return 0.0

        # Extract key terms from question (remove common words)
        common_words = {'what', 'how', 'why', 'when', 'where', 'who', 'which', 'is', 'are',
                        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
        question_words = set(word.lower().strip('?.,!')
                             for word in question.split())
        key_terms = list(question_words - common_words)
        key_terms = [term for term in key_terms if len(term) > 2]  # Filter short terms

        if not key_terms:
            return 0.0

        content_lower = content.lower()
        score = 0.0
        
        # Count term frequency and apply weighting
        for term in key_terms:
            term_count = content_lower.count(term)
            if term_count > 0:
                # Higher score for more occurrences, with diminishing returns
                score += min(term_count * 2, 10)  # Cap individual term contribution
                
                # Bonus for terms appearing early in content (more relevant)
                first_occurrence = content_lower.find(term)
                if first_occurrence < 200:  # First 200 characters
                    score += 3
                elif first_occurrence < 500:  # First 500 characters
                    score += 1

        # Normalize by content length to favor focused content
        normalized_score = score / max(len(content) / 1000, 1)  # Per 1000 characters
        
        return normalized_score

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
                if cached_data and isinstance(cached_data, bytes):
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

    def _parse_comprehensive_response(
        self, 
        response_text: str, 
        documents: List[Document]
    ) -> tuple[List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]]]:
        """Parse the comprehensive response into questions, answers, and contexts"""
        evolved_questions = []
        question_answers = []
        question_contexts = []
        

        
        try:
            # Split into sections
            lines = response_text.split('\n')
            current_section = None
            question_counter = 1
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                    
                # Section headers
                if 'SIMPLE QUESTIONS' in line.upper():
                    current_section = 'simple'
                    continue
                elif 'MULTI-CONTEXT QUESTIONS' in line.upper():
                    current_section = 'multi_context'
                    continue
                elif 'REASONING QUESTIONS' in line.upper():
                    current_section = 'reasoning'
                    continue
                
                # Parse Q/A patterns (no contexts - handled separately)
                if line.startswith(('Q', 'A')) and ':' in line:
                    prefix = line[0]
                    content = line.split(':', 1)[1].strip()
                    
                    if prefix == 'Q' and current_section:
                        # New question
                        question_id = f"fast_q_{question_counter}"
                        evolution_type = f"{current_section}_evolution"
                        complexity_level = 2 if current_section == 'simple' else 3 if current_section == 'multi_context' else 4
                        
                        evolved_questions.append({
                            "id": question_id,
                            "question": content,
                            "evolution_type": evolution_type,
                            "complexity_level": complexity_level
                        })
                        question_counter += 1
                        
                    elif prefix == 'A' and evolved_questions:
                        # Answer for last question
                        last_question = evolved_questions[-1]
                        question_answers.append({
                            "question_id": last_question["id"],
                            "answer": content
                        })
            
            # Ensure we have at least some results
            if not evolved_questions:
                # Fallback parsing for unstructured response
                question_id = "fast_fallback_1"
                evolved_questions.append({
                    "id": question_id,
                    "question": "What are the key concepts discussed in the provided documents?",
                    "evolution_type": "simple_evolution",
                    "complexity_level": 2
                })
                question_answers.append({
                    "question_id": question_id,
                    "answer": response_text[:200] + "..." if len(response_text) > 200 else response_text
                })
                # No contexts here - they'll be generated by _extract_contexts_fast()
                
        except Exception as e:
            print(f"Error parsing comprehensive response: {e}")
            # Ultra-minimal fallback
            question_id = "parse_error_1"
            evolved_questions = [{
                "id": question_id,
                "question": "What information is contained in these documents?",
                "evolution_type": "simple_evolution",
                "complexity_level": 1
            }]
            question_answers = [{
                "question_id": question_id,
                "answer": "The documents contain information that requires analysis."
            }]
            question_contexts = []  # Will be generated by _extract_contexts_fast()
        
        return evolved_questions, question_answers, question_contexts

    def _get_document_title(self, doc: Document, doc_index: int) -> str:
        """Extract proper document title from metadata"""
        # Try to get the actual filename/source
        source = doc.metadata.get('source', '')
        
        if source:
            # If source is a file path, extract just the filename
            if '/' in source or '\\' in source:
                import os
                filename = os.path.basename(source)
                # Remove file extension for cleaner display
                name_without_ext = os.path.splitext(filename)[0]
                return name_without_ext if name_without_ext else filename
            else:
                return source
        
        # If no source, try filename from metadata
        filename = doc.metadata.get('filename', '')
        if filename:
            return filename
            
        # Last resort fallback
        return f"Document {doc_index + 1}"
    
    def _create_ai_summary(self, content: str, question: str, doc_source: str) -> str:
        """Create AI-generated summary of context in under 200 words"""
        try:
            llm = self.llm_pool[0]  # Get LLM from pool
            
            summary_prompt = ChatPromptTemplate.from_template("""
            Create a concise summary of the following content that specifically relates to this question. 
            The summary MUST be under 200 words and focus only on information relevant to answering the question.
            
            Question: {question}
            Content: {content}
            Source: {source}
            
            Instructions:
            - Keep under 200 words
            - Focus only on content relevant to the question
            - Use clear, concise language
            - Include key facts and details that help answer the question
            - Do not include irrelevant information
            
            Summary:""")
            
            response = llm.invoke(summary_prompt.format(
                question=question,
                content=content[:1500],  # Limit input content for faster processing
                source=doc_source
            ))
            
            summary = str(response.content).strip() if hasattr(response, 'content') else str(response).strip()
            
            # Ensure it's under 200 words
            words = summary.split()
            if len(words) > 200:
                summary = ' '.join(words[:200]) + "..."
            
            return summary
            
        except Exception as e:
            print(f"Error creating AI summary: {e}")
            # Fallback to truncated content
            words = content.split()
            if len(words) > 50:
                return ' '.join(words[:50]) + "..."
            return content
