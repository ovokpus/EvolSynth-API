"""
EvaluationService - Service for evaluating synthetic data quality
"""

import uuid
import time
from typing import List, Dict, Any, Optional
from datetime import datetime

from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate

from api.config import settings


class EvaluationService:
    """Service for evaluating synthetic data quality using LLM-as-judge"""
    
    def __init__(self):
        """Initialize the evaluation service"""
        self.evaluation_llm = ChatOpenAI(
            model=settings.evaluation_model,
            temperature=0.1  # Low temperature for consistent evaluation
        )
        
        # Evaluation prompts
        self.evaluation_prompts = {
            "question_quality": """
            You are an expert evaluator assessing the quality of evolved questions in an AI evaluation context.

            Evaluate this evolved question for quality and appropriateness:

            Question: {question}
            Evolution Type: {evolution_type}

            Criteria to assess:
            1. Question clarity and specificity
            2. Appropriate complexity for the evolution type
            3. Educational/evaluation value
            4. Grammatical correctness

            Respond with either "GOOD" if the question meets high quality standards for AI evaluation, or "POOR" if it does not.

            Evaluation:""",
            
            "answer_accuracy": """
            You are an expert evaluator assessing answer quality.

            Question: {question}
            Generated Answer: {answer}

            Evaluate if this answer is accurate, complete, and well-structured.
            Respond with "ACCURATE" if the answer meets high quality standards, or "INACCURATE" if not.

            Evaluation:""",
            
            "evolution_effectiveness": """
            You are an expert in cognitive assessment and question design.

            Analyze this evolved question for effectiveness:

            Question: {question}
            Evolution Type: {evolution_type}
            Claimed Complexity Level: {complexity_level}

            Assess if the evolution type successfully created appropriate cognitive complexity:
            - Simple Evolution: Should enhance clarity while maintaining answerability
            - Multi-Context Evolution: Should require synthesis across multiple information sources  
            - Reasoning Evolution: Should demand logical inference and multi-step thinking

            Respond with "EFFECTIVE" if the evolution successfully achieved its cognitive goals, or "INEFFECTIVE" if not.

            Evaluation:"""
        }
    
    def evaluate_synthetic_data(
        self,
        evolved_questions: List[Dict[str, Any]],
        question_answers: List[Dict[str, Any]],
        question_contexts: List[Dict[str, Any]],
        evaluation_metrics: List[str]
    ) -> Dict[str, Any]:
        """
        Evaluate synthetic data using specified metrics
        
        Args:
            evolved_questions: List of evolved questions
            question_answers: List of question-answer pairs
            question_contexts: List of question-context mappings
            evaluation_metrics: List of metrics to evaluate
            
        Returns:
            Dictionary containing evaluation results
        """
        evaluation_id = str(uuid.uuid4())
        start_time = time.time()
        
        # Create mappings for efficient lookup
        answer_map = {qa["question_id"]: qa["answer"] for qa in question_answers}
        context_map = {qc["question_id"]: qc["contexts"] for qc in question_contexts}
        
        detailed_results = []
        metric_scores = {metric: [] for metric in evaluation_metrics}
        
        # Evaluate each question
        for question in evolved_questions:
            question_id = question["id"]
            question_result = {"question_id": question_id}
            
            # Get associated answer and contexts
            answer = answer_map.get(question_id, "")
            contexts = context_map.get(question_id, [])
            
            # Evaluate each metric
            for metric in evaluation_metrics:
                score = self._evaluate_single_metric(question, answer, contexts, metric)
                question_result[metric] = score
                metric_scores[metric].append(score)
            
            detailed_results.append(question_result)
        
        # Calculate overall scores
        overall_scores = {}
        for metric, scores in metric_scores.items():
            overall_scores[metric] = sum(scores) / len(scores) if scores else 0.0
        
        # Generate summary statistics
        summary_statistics = self._generate_summary_statistics(evolved_questions, detailed_results)
        
        end_time = time.time()
        
        return {
            "success": True,
            "evaluation_id": evaluation_id,
            "overall_scores": overall_scores,
            "detailed_results": detailed_results,
            "summary_statistics": summary_statistics,
            "evaluation_time_seconds": end_time - start_time,
            "timestamp": datetime.now()
        }
    
    def _evaluate_single_metric(
        self,
        question: Dict[str, Any],
        answer: str,
        contexts: List[str],
        metric: str
    ) -> float:
        """Evaluate a single metric for a question"""
        try:
            if metric == "question_quality":
                return self._evaluate_question_quality(question)
            elif metric == "answer_accuracy":
                return self._evaluate_answer_accuracy(question, answer)
            elif metric == "evolution_effectiveness":
                return self._evaluate_evolution_effectiveness(question)
            else:
                return 0.0
        except Exception as e:
            print(f"Error evaluating metric {metric}: {e}")
            return 0.0
    
    def _evaluate_question_quality(self, question: Dict[str, Any]) -> float:
        """Evaluate question quality using LLM-as-judge"""
        prompt = ChatPromptTemplate.from_template(self.evaluation_prompts["question_quality"])
        
        response = self.evaluation_llm.invoke(
            prompt.format_messages(
                question=question["question"],
                evolution_type=question.get("evolution_type", "unknown")
            )
        )
        
        evaluation = str(response.content).strip() if hasattr(response, 'content') else str(response).strip()
        return 1.0 if "GOOD" in evaluation.upper() else 0.0
    
    def _evaluate_answer_accuracy(self, question: Dict[str, Any], answer: str) -> float:
        """Evaluate answer accuracy using LLM-as-judge"""
        if not answer:
            return 0.0
        
        prompt = ChatPromptTemplate.from_template(self.evaluation_prompts["answer_accuracy"])
        
        response = self.evaluation_llm.invoke(
            prompt.format_messages(
                question=question["question"],
                answer=answer
            )
        )
        
        evaluation = str(response.content).strip() if hasattr(response, 'content') else str(response).strip()
        return 1.0 if "ACCURATE" in evaluation.upper() else 0.0
    
    def _evaluate_evolution_effectiveness(self, question: Dict[str, Any]) -> float:
        """Evaluate evolution effectiveness using LLM-as-judge"""
        prompt = ChatPromptTemplate.from_template(self.evaluation_prompts["evolution_effectiveness"])
        
        response = self.evaluation_llm.invoke(
            prompt.format_messages(
                question=question["question"],
                evolution_type=question.get("evolution_type", "unknown"),
                complexity_level=question.get("complexity_level", 1)
            )
        )
        
        evaluation = str(response.content).strip() if hasattr(response, 'content') else str(response).strip()
        return 1.0 if "EFFECTIVE" in evaluation.upper() else 0.0
    
    def _generate_summary_statistics(
        self,
        evolved_questions: List[Dict[str, Any]],
        detailed_results: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate summary statistics for the evaluation"""
        # Count evolution types
        evolution_type_distribution = {}
        complexity_levels = []
        
        for question in evolved_questions:
            evo_type = question.get("evolution_type", "unknown")
            evolution_type_distribution[evo_type] = evolution_type_distribution.get(evo_type, 0) + 1
            complexity_levels.append(question.get("complexity_level", 1))
        
        return {
            "total_questions_evaluated": len(evolved_questions),
            "average_complexity": sum(complexity_levels) / len(complexity_levels) if complexity_levels else 0,
            "evolution_type_distribution": evolution_type_distribution,
            "evaluation_coverage": len(detailed_results) / len(evolved_questions) if evolved_questions else 0
        } 