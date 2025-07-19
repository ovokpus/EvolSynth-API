"""
EvolInstructService - Core LangGraph-based Evol-Instruct Implementation
Extracted and refactored from the Bonus Activity notebook
"""

import os
import json
import random
import uuid
import time
import operator
from typing import List, Dict, Any, Optional, TypedDict, Annotated
from dataclasses import dataclass
from enum import Enum

# LangGraph imports
from langgraph.graph import StateGraph, END

# LangChain imports
from langchain.schema import Document, StrOutputParser
from langchain.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

# Local imports
from api.config import settings
from api.models.core import EvolutionType, ExecutionMode, GenerationSettings, PerformanceMetrics


class EvolInstructState(TypedDict):
    """State for the LangGraph workflow"""
    documents: List[Document]
    base_questions: List[Dict[str, Any]]
    evolved_questions: Annotated[List[Dict[str, Any]], operator.add]
    question_answers: List[Dict[str, Any]]
    question_contexts: List[Dict[str, Any]]
    current_iteration: int
    max_iterations: int


class EvolInstructService:
    """Service for generating synthetic data using LangGraph-based Evol-Instruct methodology"""
    
    def __init__(self):
        """Initialize the service with LLM and prompts"""
        self.llm = ChatOpenAI(
            model=settings.default_model,
            temperature=settings.temperature
        )
        
        # Evolution prompts from the notebook
        self.prompts = {
            "base_questions": """
            You are an expert at generating simple, foundational questions from document content.

            Given the following document content, generate 3-5 simple, factual questions that can be answered directly from the content.
            The questions should be:
            1. Clear and straightforward
            2. Answerable from the given content
            3. Cover different aspects of the content
            4. Suitable for evolution into more complex questions

            Content: {content}

            Generate questions in this format:
            1. [Question 1]
            2. [Question 2]
            3. [Question 3]
            etc.

            Questions:""",
            
            "simple_evolution": """
            You are an expert at evolving questions to make them more complex while maintaining their essence.

            Given the following context and base question, create a more complex version of the question.
            The evolved question should:
            1. Require deeper understanding of the content
            2. Be more specific and detailed
            3. Still be answerable from the given context

            Context: {context}

            Base Question: {base_question}

            Evolved Question:""",
            
            "multi_context_evolution": """
            You are an expert at creating questions that require information from multiple sources.

            Given the following contexts and base question, create a question that requires synthesizing information from multiple contexts.
            The evolved question should:
            1. Require information from at least 2 different contexts
            2. Ask for comparison, relationship, or synthesis
            3. Be more complex than the original question

            Contexts:
            {contexts}

            Base Question: {base_question}

            Evolved Question:""",
            
            "reasoning_evolution": """
            You are an expert at creating questions that require multi-step reasoning.

            Given the following context and base question, create a question that requires logical reasoning, inference, or multi-step thinking.
            The evolved question should:
            1. Require the reader to make logical connections
            2. Involve cause-and-effect relationships or implications
            3. Require step-by-step reasoning to answer

            Context: {context}

            Base Question: {base_question}

            Evolved Question:""",
            
            "answer_generation": """
            You are an expert at answering questions based on provided context.

            Given the following context(s) and question, provide a comprehensive and accurate answer.
            Base your answer strictly on the information provided in the context(s).

            Context(s):
            {contexts}

            Question: {question}

            Answer:"""
        }
        
        # Initialize workflow graphs
        self._concurrent_graph = None
        self._sequential_graph = None
    
    def generate_synthetic_data(
        self, 
        documents: List[Document], 
        settings: Optional[GenerationSettings] = None,
        max_iterations: int = 1
    ) -> Dict[str, Any]:
        """
        Generate synthetic data using the LangGraph-based Evol-Instruct workflow
        
        Args:
            documents: List of input documents
            settings: Generation settings (uses defaults if None)
            max_iterations: Maximum iterations for generation
            
        Returns:
            Dictionary containing generated synthetic data and performance metrics
        """
        if settings is None:
            settings = GenerationSettings()
        
        # Initialize state
        initial_state: EvolInstructState = {
            "documents": documents,
            "base_questions": [],
            "evolved_questions": [],
            "question_answers": [],
            "question_contexts": [],
            "current_iteration": 0,
            "max_iterations": max_iterations
        }
        
        # Select and compile graph based on execution mode
        if settings.execution_mode == ExecutionMode.CONCURRENT:
            graph = self._get_concurrent_graph()
        else:
            graph = self._get_sequential_graph()
        
        # Execute generation with timing
        start_time = time.time()
        final_state = graph.invoke(initial_state)
        end_time = time.time()
        
        execution_time = end_time - start_time
        
        # Calculate performance metrics
        performance_metrics = PerformanceMetrics(
            execution_time_seconds=execution_time,
            questions_generated=len(final_state["evolved_questions"]),
            answers_generated=len(final_state["question_answers"]),
            contexts_extracted=len(final_state["question_contexts"]),
            questions_per_second=len(final_state["evolved_questions"]) / execution_time if execution_time > 0 else 0,
            execution_mode=settings.execution_mode.value
        )
        
        # Format final output
        return {
            "evolved_questions": final_state["evolved_questions"],
            "question_answers": final_state["question_answers"],
            "question_contexts": final_state["question_contexts"],
            "performance_metrics": performance_metrics,
            "generation_id": str(uuid.uuid4()),
            "settings_used": settings.dict()
        }
    
    def _get_concurrent_graph(self):
        """Get or create the concurrent execution graph"""
        if self._concurrent_graph is None:
            self._concurrent_graph = self._create_concurrent_graph()
        return self._concurrent_graph
    
    def _get_sequential_graph(self):
        """Get or create the sequential execution graph"""
        if self._sequential_graph is None:
            self._sequential_graph = self._create_sequential_graph()
        return self._sequential_graph
    
    def _create_concurrent_graph(self):
        """Create the concurrent execution graph (fan-out/fan-in pattern)"""
        workflow = StateGraph(EvolInstructState)
        
        # Add nodes
        workflow.add_node("generate_base_questions", self._generate_base_questions_node)
        workflow.add_node("simple_evolution", self._simple_evolution_node)
        workflow.add_node("multi_context_evolution", self._multi_context_evolution_node)
        workflow.add_node("reasoning_evolution", self._reasoning_evolution_node)
        workflow.add_node("generate_answers", self._generate_answers_node)
        workflow.add_node("extract_contexts", self._extract_contexts_node)
        
        # Define concurrent flow (fan-out/fan-in)
        workflow.set_entry_point("generate_base_questions")
        
        # Fan-out: All evolution types run concurrently
        workflow.add_edge("generate_base_questions", "simple_evolution")
        workflow.add_edge("generate_base_questions", "multi_context_evolution")
        workflow.add_edge("generate_base_questions", "reasoning_evolution")
        
        # Fan-in: Wait for all evolution types to complete
        workflow.add_edge(["simple_evolution", "multi_context_evolution", "reasoning_evolution"], "generate_answers")
        workflow.add_edge("generate_answers", "extract_contexts")
        workflow.add_edge("extract_contexts", END)
        
        return workflow.compile()
    
    def _create_sequential_graph(self):
        """Create the sequential execution graph"""
        workflow = StateGraph(EvolInstructState)
        
        # Add nodes
        workflow.add_node("generate_base_questions", self._generate_base_questions_node)
        workflow.add_node("simple_evolution", self._simple_evolution_node)
        workflow.add_node("multi_context_evolution", self._multi_context_evolution_node)
        workflow.add_node("reasoning_evolution", self._reasoning_evolution_node)
        workflow.add_node("generate_answers", self._generate_answers_node)
        workflow.add_node("extract_contexts", self._extract_contexts_node)
        
        # Define sequential flow
        workflow.set_entry_point("generate_base_questions")
        workflow.add_edge("generate_base_questions", "simple_evolution")
        workflow.add_edge("simple_evolution", "multi_context_evolution")
        workflow.add_edge("multi_context_evolution", "reasoning_evolution")
        workflow.add_edge("reasoning_evolution", "generate_answers")
        workflow.add_edge("generate_answers", "extract_contexts")
        workflow.add_edge("extract_contexts", END)
        
        return workflow.compile()
    
    def _generate_base_questions_node(self, state: EvolInstructState) -> EvolInstructState:
        """Generate base questions from documents"""
        base_questions = []
        
        for i, doc in enumerate(state["documents"]):
            prompt = ChatPromptTemplate.from_template(self.prompts["base_questions"])
            
            response = self.llm.invoke(
                prompt.format_messages(content=doc.page_content[:settings.max_content_length])
            )
            
            # Parse questions
            questions_text = str(response.content) if hasattr(response, 'content') else str(response)
            questions = self._parse_questions(questions_text)
            
            # Add questions with metadata
            for question in questions[:settings.max_base_questions_per_doc]:
                base_questions.append({
                    "id": str(uuid.uuid4()),
                    "question": question,
                    "source_doc_index": i,
                    "context": doc.page_content
                })
        
        state["base_questions"] = base_questions
        return state
    
    def _simple_evolution_node(self, state: EvolInstructState) -> Dict[str, Any]:
        """Apply simple evolution to base questions"""
        return self._evolution_node(state, EvolutionType.SIMPLE, settings.simple_evolution_count)
    
    def _multi_context_evolution_node(self, state: EvolInstructState) -> Dict[str, Any]:
        """Apply multi-context evolution to base questions"""
        return self._evolution_node(state, EvolutionType.MULTI_CONTEXT, settings.multi_context_evolution_count)
    
    def _reasoning_evolution_node(self, state: EvolInstructState) -> Dict[str, Any]:
        """Apply reasoning evolution to base questions"""
        return self._evolution_node(state, EvolutionType.REASONING, settings.reasoning_evolution_count)
    
    def _evolution_node(self, state: EvolInstructState, evolution_type: EvolutionType, count: int) -> Dict[str, Any]:
        """Generic evolution node implementation"""
        new_evolved_questions = []
        
        # Select random base questions for evolution
        questions_to_evolve = random.sample(
            state["base_questions"], 
            min(count, len(state["base_questions"]))
        )
        
        for base_q in questions_to_evolve:
            if evolution_type == EvolutionType.MULTI_CONTEXT:
                evolved_q = self._evolve_multi_context_question(base_q, state["documents"])
            else:
                evolved_q = self._evolve_single_context_question(base_q, evolution_type)
            
            if evolved_q:
                new_evolved_questions.append(evolved_q)
        
        return {"evolved_questions": new_evolved_questions}
    
    def _evolve_single_context_question(self, base_q: Dict[str, Any], evolution_type: EvolutionType) -> Optional[Dict[str, Any]]:
        """Evolve a question using single context"""
        prompt_key = evolution_type.value
        prompt = ChatPromptTemplate.from_template(self.prompts[prompt_key])
        
        response = self.llm.invoke(
            prompt.format_messages(
                context=base_q["context"][:1500],
                base_question=base_q["question"]
            )
        )
        
        complexity_levels = {
            EvolutionType.SIMPLE: 2,
            EvolutionType.REASONING: 4
        }
        
        return {
            "id": str(uuid.uuid4()),
            "question": str(response.content).strip() if hasattr(response, 'content') else str(response).strip(),
            "evolution_type": evolution_type.value,
            "source_context_ids": [base_q["id"]],
            "complexity_level": complexity_levels.get(evolution_type, 2)
        }
    
    def _evolve_multi_context_question(self, base_q: Dict[str, Any], documents: List[Document]) -> Optional[Dict[str, Any]]:
        """Evolve a question using multiple contexts"""
        # Select additional contexts from other documents
        other_docs = [doc for i, doc in enumerate(documents) if i != base_q["source_doc_index"]]
        
        if not other_docs:
            return None
        
        additional_context = random.choice(other_docs).page_content[:1000]
        combined_contexts = f"Context 1:\n{base_q['context'][:1000]}\n\nContext 2:\n{additional_context}"
        
        prompt = ChatPromptTemplate.from_template(self.prompts["multi_context_evolution"])
        
        response = self.llm.invoke(
            prompt.format_messages(
                contexts=combined_contexts,
                base_question=base_q["question"]
            )
        )
        
        return {
            "id": str(uuid.uuid4()),
            "question": str(response.content).strip() if hasattr(response, 'content') else str(response).strip(),
            "evolution_type": EvolutionType.MULTI_CONTEXT.value,
            "source_context_ids": [base_q["id"], "additional_context"],
            "complexity_level": 3
        }
    
    def _generate_answers_node(self, state: EvolInstructState) -> EvolInstructState:
        """Generate answers for all evolved questions"""
        question_answers = []
        
        for evolved_q in state["evolved_questions"]:
            # Get relevant contexts
            contexts = self._get_contexts_for_question(evolved_q, state)
            combined_contexts = "\n\n".join(f"Context {i+1}:\n{ctx}" for i, ctx in enumerate(contexts))
            
            # Generate answer
            prompt = ChatPromptTemplate.from_template(self.prompts["answer_generation"])
            response = self.llm.invoke(
                prompt.format_messages(
                    contexts=combined_contexts,
                    question=evolved_q["question"]
                )
            )
            
            answer = {
                "question_id": evolved_q["id"],
                "answer": str(response.content).strip() if hasattr(response, 'content') else str(response).strip()
            }
            question_answers.append(answer)
        
        state["question_answers"] = question_answers
        return state
    
    def _extract_contexts_node(self, state: EvolInstructState) -> EvolInstructState:
        """Extract and organize contexts for each question"""
        question_contexts = []
        
        for evolved_q in state["evolved_questions"]:
            contexts = self._get_contexts_for_question(evolved_q, state)
            
            question_context = {
                "question_id": evolved_q["id"],
                "contexts": contexts
            }
            question_contexts.append(question_context)
        
        state["question_contexts"] = question_contexts
        return state
    
    def _get_contexts_for_question(self, evolved_q: Dict[str, Any], state: EvolInstructState) -> List[str]:
        """Get relevant contexts for a question"""
        contexts = []
        
        if evolved_q["evolution_type"] == EvolutionType.MULTI_CONTEXT.value:
            # For multi-context questions, use multiple document contexts
            base_context = next(
                (bq["context"] for bq in state["base_questions"] 
                 if bq["id"] in evolved_q["source_context_ids"]), 
                ""
            )
            contexts.append(base_context[:1000])
            
            # Add additional context from other documents
            other_docs = [doc for doc in state["documents"]]
            if other_docs:
                additional_context = random.choice(other_docs).page_content[:1000]
                contexts.append(additional_context)
        else:
            # For simple and reasoning questions, use the original context
            base_context = next(
                (bq["context"] for bq in state["base_questions"] 
                 if bq["id"] in evolved_q["source_context_ids"]), 
                ""
            )
            contexts.append(base_context[:1500])
        
        return contexts
    
    def _parse_questions(self, questions_text: str) -> List[str]:
        """Parse questions from LLM response"""
        questions = []
        
        for line in questions_text.split('\n'):
            if line.strip() and (line.strip().startswith(tuple('123456789')) or line.strip().startswith('-')):
                # Clean up the question
                question = line.split('.', 1)[-1].strip() if '.' in line else line.strip()
                question = question.lstrip('- ').strip()
                if question and question.endswith('?'):
                    questions.append(question)
        
        return questions 