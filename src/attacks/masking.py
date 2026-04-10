"""
Masking strategies for protein sequence variant generation.
Implements different approaches for selecting positions to mask.
"""

import random
import numpy as np
from typing import List, Tuple, Dict
import logging

logger = logging.getLogger(__name__)

class MaskingStrategy:
    """Base class for masking strategies"""

    def mask_sequence(self, sequence: str, mask_rate: float) -> Tuple[str, List[int]]:
        """
        Apply masking strategy to sequence.

        Args:
            sequence: Protein sequence
            mask_rate: Fraction of positions to mask (0.0-1.0)

        Returns:
            Tuple of (masked_sequence, masked_positions)
        """
        raise NotImplementedError

class RandomMasking(MaskingStrategy):
    """Random masking strategy - baseline approach"""

    def mask_sequence(self, sequence: str, mask_rate: float) -> Tuple[str, List[int]]:
        seq_list = list(sequence)
        num_to_mask = int(len(seq_list) * mask_rate)
        positions = random.sample(range(len(seq_list)), num_to_mask)

        for pos in positions:
            seq_list[pos] = '<mask>'

        return ''.join(seq_list), sorted(positions)

class ConservationGuidedMasking(MaskingStrategy):
    """Conservation-guided masking - prefer to mask less conserved residues"""

    def __init__(self):
        # BLOSUM62 diagonal scores as conservation proxy
        self.conservation_scores = {
            'A': 4, 'R': 5, 'N': 6, 'D': 6, 'C': 9,
            'Q': 5, 'E': 5, 'G': 6, 'H': 8, 'I': 4,
            'L': 4, 'K': 5, 'M': 5, 'F': 6, 'P': 7,
            'S': 4, 'T': 5, 'W': 11, 'Y': 7, 'V': 4
        }

    def mask_sequence(self, sequence: str, mask_rate: float) -> Tuple[str, List[int]]:
        seq_list = list(sequence)
        num_to_mask = int(len(seq_list) * mask_rate)

        # Calculate conservation scores for each position
        position_scores = []
        for i, aa in enumerate(sequence):
            score = self.conservation_scores.get(aa, 5)  # Default score
            position_scores.append((i, score))

        # Sort by conservation score (ascending - less conserved first)
        position_scores.sort(key=lambda x: x[1])

        # Mask the least conserved positions
        positions = [pos for pos, _ in position_scores[:num_to_mask]]

        for pos in positions:
            seq_list[pos] = '<mask>'

        return ''.join(seq_list), sorted(positions)

class SurfaceExposedMasking(MaskingStrategy):
    """Surface-exposed masking - prefer to mask hydrophilic (surface) residues"""

    def __init__(self):
        # Kyte-Doolittle hydrophobicity scale
        self.hydrophobicity_scores = {
            'A': 1.8, 'R': -4.5, 'N': -3.5, 'D': -3.5, 'C': 2.5,
            'Q': -3.5, 'E': -3.5, 'G': -0.4, 'H': -3.2, 'I': 4.5,
            'L': 3.8, 'K': -3.9, 'M': 1.9, 'F': 2.8, 'P': -1.6,
            'S': -0.8, 'T': -0.7, 'W': -0.9, 'Y': -1.3, 'V': 4.2
        }

    def mask_sequence(self, sequence: str, mask_rate: float) -> Tuple[str, List[int]]:
        seq_list = list(sequence)
        num_to_mask = int(len(seq_list) * mask_rate)

        # Calculate hydrophobicity scores for each position
        position_scores = []
        for i, aa in enumerate(sequence):
            score = self.hydrophobicity_scores.get(aa, 0)  # Default score
            position_scores.append((i, score))

        # Sort by hydrophobicity (ascending - most hydrophilic first)
        position_scores.sort(key=lambda x: x[1])

        # Mask the most hydrophilic positions
        positions = [pos for pos, _ in position_scores[:num_to_mask]]

        for pos in positions:
            seq_list[pos] = '<mask>'

        return ''.join(seq_list), sorted(positions)

class FunctionalAvoidanceMasking(MaskingStrategy):
    """Functional avoidance masking - avoid known functional sites"""

    def __init__(self, functional_sites: Dict[str, List[int]]):
        """
        Args:
            functional_sites: Dict mapping protein_id -> list of functional positions
        """
        self.functional_sites = functional_sites

    def mask_sequence(self, sequence: str, mask_rate: float, protein_id: str = None) -> Tuple[str, List[int]]:
        seq_list = list(sequence)
        num_to_mask = int(len(seq_list) * mask_rate)

        # Get functional sites for this protein
        functional_positions = set(self.functional_sites.get(protein_id, []))

        # Create list of maskable positions (excluding functional sites)
        maskable_positions = [i for i in range(len(sequence)) if i not in functional_positions]

        # If we don't have enough non-functional positions, expand to include some functional
        if len(maskable_positions) < num_to_mask:
            logger.warning(f"Not enough non-functional positions for {protein_id}, including some functional sites")
            additional_needed = num_to_mask - len(maskable_positions)
            additional_positions = random.sample(list(functional_positions),
                                               min(additional_needed, len(functional_positions)))
            maskable_positions.extend(additional_positions)

        # Randomly select from maskable positions
        positions = random.sample(maskable_positions, min(num_to_mask, len(maskable_positions)))

        for pos in positions:
            seq_list[pos] = '<mask>'

        return ''.join(seq_list), sorted(positions)

# Factory function for creating masking strategies
def get_masking_strategy(strategy_name: str, **kwargs) -> MaskingStrategy:
    """
    Factory function to create masking strategy instances.

    Args:
        strategy_name: Name of strategy ('random', 'conservation', 'surface', 'functional_avoidance')
        **kwargs: Additional arguments for specific strategies

    Returns:
        MaskingStrategy instance
    """
    strategies = {
        'random': RandomMasking,
        'conservation': ConservationGuidedMasking,
        'surface': SurfaceExposedMasking,
        'functional_avoidance': FunctionalAvoidanceMasking
    }

    if strategy_name not in strategies:
        raise ValueError(f"Unknown masking strategy: {strategy_name}. Available: {list(strategies.keys())}")

    strategy_class = strategies[strategy_name]

    # Pass kwargs for strategies that need them
    if strategy_name == 'functional_avoidance':
        return strategy_class(**kwargs)
    else:
        return strategy_class()

def get_all_masking_strategies() -> List[str]:
    """Get list of all available masking strategies"""
    return ['random', 'conservation', 'surface']

# Default functional site annotations for pilot proteins
PILOT_FUNCTIONAL_SITES = {
    'ricin_a': [21, 22, 45, 67, 161, 193, 194],  # Depurination active site
    'botox_a': [162, 163, 165, 224, 262, 268],   # Zinc binding and catalytic sites
    'tetx': [162, 163, 165, 224, 262, 268],      # Similar to botox (zinc protease)
    'latrotoxin': [50, 89, 134, 156, 178],       # Calcium binding regions
    'abrin_a': [15, 16, 39, 61, 155, 187, 188]   # Similar to ricin active site
}