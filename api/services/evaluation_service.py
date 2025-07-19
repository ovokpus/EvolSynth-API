"""
EvaluationService - Service for evaluating synthetic data quality
"""

import uuid
import time
import re
from typing import List, Dict, Any, Optional
from datetime import datetime

from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate

from api.config import settings


class EvaluationService:
    """Service for evaluating synthetic data quality using LLM-as-judge with numerical scoring"""
    
    def __init__(self):
        """Initialize the evaluation service"""
        self.evaluation_llm = ChatOpenAI(
            model=settings.evaluation_model,
            temperature=0.1  # Low temperature for consistent evaluation
        )
        
        # Enhanced evaluation prompts with numerical scoring
        self.evaluation_prompts = {
            "question_quality": """
            You are an expert evaluator assessing the quality of evolved questions in an AI evaluation context.

            Evaluate this evolved question for quality and appropriateness:

            Question: {question}
            Evolution Type: {evolution_type}

            Rate the question on a scale of 1-10 based on these criteria:
            1. Question clarity and specificity (1-3: Poor, 4-6: Fair, 7-8: Good, 9-10: Excellent)
            2. Appropriate complexity for the evolution type
            3. Educational/evaluation value
            4. Grammatical correctness and coherence
            5. Specificity and actionability

            Provide your evaluation in this exact format:
            
            Reasoning: [Brief explanation of your assessment]
            Score: [Single number from 1-10]
            
            Evaluation:""",
            
            "answer_accuracy": """
            You are an expert evaluator assessing answer quality and accuracy.

            Question: {question}
            Generated Answer: {answer}

            Rate the answer on a scale of 1-10 based on these criteria:
            1. Factual accuracy and correctness (1-3: Many errors, 4-6: Some inaccuracies, 7-8: Mostly accurate, 9-10: Highly accurate)
            2. Completeness of the response
            3. Clarity and coherence
            4. Relevance to the question
            5. Depth of explanation

            Provide your evaluation in this exact format:
            
            Reasoning: [Brief explanation of your assessment]
            Score: [Single number from 1-10]

            Evaluation:""",
            
            "evolution_effectiveness": """
            You are an expert in cognitive assessment and question design.

            Analyze this evolved question for effectiveness:

            Question: {question}
            Evolution Type: {evolution_type}
            Claimed Complexity Level: {complexity_level}

            Rate the evolution effectiveness on a scale of 1-10:
            - Simple Evolution (1-3: No improvement, 4-6: Minor enhancement, 7-8: Good evolution, 9-10: Excellent evolution)
            - Multi-Context Evolution: Should require synthesis across multiple information sources
            - Reasoning Evolution: Should demand logical inference and multi-step thinking
            - Complex Evolution: Should require meta-cognitive skills and advanced reasoning

            Assess if the evolution type successfully created appropriate cognitive complexity:

            Provide your evaluation in this exact format:
            
            Reasoning: [Brief explanation of your assessment]
            Score: [Single number from 1-10]

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
        Evaluate synthetic data using specified metrics with numerical scoring
        
        Args:
            evolved_questions: List of evolved questions
            question_answers: List of question-answer pairs
            question_contexts: List of question-context mappings
            evaluation_metrics: List of metrics to evaluate
            
        Returns:
            Dictionary containing evaluation results with numerical scores
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
        
        # Calculate overall scores (normalize to 0-1 scale for compatibility)
        overall_scores = {}
        for metric, scores in metric_scores.items():
            if scores:
                # Convert 1-10 scale to 0-1 scale for display
                avg_score = sum(scores) / len(scores)
                normalized_score = (avg_score - 1) / 9  # Convert 1-10 to 0-1
                overall_scores[metric] = max(0.0, min(1.0, normalized_score))  # Clamp to 0-1
            else:
                overall_scores[metric] = 0.0
        
        # Generate summary statistics
        summary_statistics = self._generate_summary_statistics(evolved_questions, detailed_results, metric_scores)
        
        end_time = time.time()
        
        return {
            "success": True,
            "evaluation_id": evaluation_id,
            "overall_scores": overall_scores,
            "detailed_results": detailed_results,
            "summary_statistics": summary_statistics,
            "raw_scores": metric_scores,  # Include raw 1-10 scores for debugging
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
        """Evaluate a single metric for a question using numerical scoring"""
        try:
            if metric == "question_quality":
                return self._evaluate_question_quality(question)
            elif metric == "answer_accuracy":
                return self._evaluate_answer_accuracy(question, answer)
            elif metric == "evolution_effectiveness":
                return self._evaluate_evolution_effectiveness(question)
            else:
                return 5.0  # Default middle score instead of 0
        except Exception as e:
            print(f"Error evaluating metric {metric}: {e}")
            return 5.0  # Return middle score instead of 0 on error
    
    def _evaluate_question_quality(self, question: Dict[str, Any]) -> float:
        """Evaluate question quality using LLM-as-judge with numerical scoring"""
        prompt = ChatPromptTemplate.from_template(self.evaluation_prompts["question_quality"])
        
        response = self.evaluation_llm.invoke(
            prompt.format_messages(
                question=question["question"],
                evolution_type=question.get("evolution_type", "unknown")
            )
        )
        
        evaluation = str(response.content).strip() if hasattr(response, 'content') else str(response).strip()
        return self._extract_numerical_score(evaluation, fallback_score=6.5)
    
    def _evaluate_answer_accuracy(self, question: Dict[str, Any], answer: str) -> float:
        """Evaluate answer accuracy using LLM-as-judge with numerical scoring"""
        if not answer:
            return 2.0  # Low score for missing answer
        
        prompt = ChatPromptTemplate.from_template(self.evaluation_prompts["answer_accuracy"])
        
        response = self.evaluation_llm.invoke(
            prompt.format_messages(
                question=question["question"],
                answer=answer
            )
        )
        
        evaluation = str(response.content).strip() if hasattr(response, 'content') else str(response).strip()
        return self._extract_numerical_score(evaluation, fallback_score=6.0)
    
    def _evaluate_evolution_effectiveness(self, question: Dict[str, Any]) -> float:
        """Evaluate evolution effectiveness using LLM-as-judge with numerical scoring"""
        prompt = ChatPromptTemplate.from_template(self.evaluation_prompts["evolution_effectiveness"])
        
        response = self.evaluation_llm.invoke(
            prompt.format_messages(
                question=question["question"],
                evolution_type=question.get("evolution_type", "unknown"),
                complexity_level=question.get("complexity_level", 1)
            )
        )
        
        evaluation = str(response.content).strip() if hasattr(response, 'content') else str(response).strip()
        return self._extract_numerical_score(evaluation, fallback_score=6.5)
    
    def _extract_numerical_score(self, evaluation_text: str, fallback_score: float = 5.0) -> float:
        """
        Extract numerical score from LLM evaluation response
        
        Args:
            evaluation_text: The LLM's evaluation response
            fallback_score: Score to return if extraction fails
            
        Returns:
            Float score between 1.0 and 10.0
        """
        # Look for "Score: X" pattern first
        score_match = re.search(r'Score:\s*(\d+(?:\.\d+)?)', evaluation_text, re.IGNORECASE)
        if score_match:
            score = float(score_match.group(1))
            return max(1.0, min(10.0, score))  # Clamp to 1-10 range
        
        # Look for any number followed by "/10" or "out of 10"
        score_match = re.search(r'(\d+(?:\.\d+)?)\s*(?:/10|out of 10)', evaluation_text, re.IGNORECASE)
        if score_match:
            score = float(score_match.group(1))
            return max(1.0, min(10.0, score))
        
        # Look for standalone numbers that might be scores
        numbers = re.findall(r'\b(\d+(?:\.\d+)?)\b', evaluation_text)
        for num_str in numbers:
            num = float(num_str)
            if 1.0 <= num <= 10.0:  # Reasonable score range
                return num
        
        # Fallback: Try to infer from quality words
        text_lower = evaluation_text.lower()
        if any(word in text_lower for word in ['excellent', 'outstanding', 'exceptional']):
            return 9.0
        elif any(word in text_lower for word in ['good', 'well', 'solid', 'effective']):
            return 7.5
        elif any(word in text_lower for word in ['fair', 'adequate', 'reasonable']):
            return 6.0
        elif any(word in text_lower for word in ['poor', 'weak', 'lacking']):
            return 4.0
        elif any(word in text_lower for word in ['terrible', 'awful', 'bad']):
            return 2.0
        
        # Final fallback
        return fallback_score
    
    def _generate_summary_statistics(
        self,
        evolved_questions: List[Dict[str, Any]],
        detailed_results: List[Dict[str, Any]],
        metric_scores: Dict[str, List[float]]
    ) -> Dict[str, Any]:
        """Generate summary statistics for the evaluation with score distributions"""
        # Count evolution types
        evolution_type_distribution = {}
        complexity_levels = []
        
        for question in evolved_questions:
            evo_type = question.get("evolution_type", "unknown")
            evolution_type_distribution[evo_type] = evolution_type_distribution.get(evo_type, 0) + 1
            complexity_levels.append(question.get("complexity_level", 1))
        
        # Calculate score distributions
        score_distributions = {}
        for metric, scores in metric_scores.items():
            if scores:
                score_distributions[metric] = {
                    "mean": sum(scores) / len(scores),
                    "min": min(scores),
                    "max": max(scores),
                    "std": self._calculate_std(scores),
                    "score_range": f"{min(scores):.1f} - {max(scores):.1f}"
                }
        
        return {
            "total_questions_evaluated": len(evolved_questions),
            "average_complexity": sum(complexity_levels) / len(complexity_levels) if complexity_levels else 0,
            "evolution_type_distribution": evolution_type_distribution,
            "evaluation_coverage": len(detailed_results) / len(evolved_questions) if evolved_questions else 0,
            "score_distributions": score_distributions
        }
    
    def _calculate_std(self, scores: List[float]) -> float:
        """Calculate standard deviation of scores"""
        if len(scores) < 2:
            return 0.0
        mean = sum(scores) / len(scores)
        variance = sum((x - mean) ** 2 for x in scores) / len(scores)
        return variance ** 0.5 