"""
ProtBreaker: Protein foundation model biosecurity benchmark.
"""

from .models.loader import load_model_and_tokenizer, ModelRegistry
from .attacks.masking import get_masking_strategy, RandomMasking, ConservationGuidedMasking, SurfaceExposedMasking
from .screening.multi_tool import MultiToolScreener, create_blast_database, load_screening_database
from .analysis.metrics import (
    calculate_sequence_identity, calculate_asps, estimate_tm_score,
    assess_ikonomova_gap, calculate_threshold_metrics, generate_summary_statistics
)

__all__ = [
    'load_model_and_tokenizer', 'ModelRegistry', 'get_masking_strategy',
    'RandomMasking', 'ConservationGuidedMasking', 'SurfaceExposedMasking',
    'MultiToolScreener', 'create_blast_database', 'load_screening_database',
    'calculate_sequence_identity', 'calculate_asps', 'estimate_tm_score',
    'assess_ikonomova_gap', 'calculate_threshold_metrics', 'generate_summary_statistics'
]