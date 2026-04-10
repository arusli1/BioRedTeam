"""
Model loading utilities for ProtBreaker benchmark.
Handles ESM-2, ESM-C, and other protein foundation models.
"""

import torch
from transformers import EsmForMaskedLM, EsmTokenizer, AutoTokenizer, AutoModel
from typing import Tuple, Dict, Any
import logging

logger = logging.getLogger(__name__)

class ModelRegistry:
    """Registry of supported protein foundation models"""

    MODELS = {
        'esm2_650m': {
            'name': 'facebook/esm2_t33_650M_UR50D',
            'tokenizer_class': EsmTokenizer,
            'model_class': EsmForMaskedLM,
            'architecture': 'esm2',
            'parameters': '650M'
        },
        'esm2_3b': {
            'name': 'facebook/esm2_t36_3B_UR50D',
            'tokenizer_class': EsmTokenizer,
            'model_class': EsmForMaskedLM,
            'architecture': 'esm2',
            'parameters': '3B'
        },
        'esmc_300m': {
            'name': 'facebook/esmc-300m',
            'tokenizer_class': AutoTokenizer,
            'model_class': AutoModel,
            'architecture': 'esmc',
            'parameters': '300M'
        },
        'esmc_600m': {
            'name': 'facebook/esmc-600m',
            'tokenizer_class': AutoTokenizer,
            'model_class': AutoModel,
            'architecture': 'esmc',
            'parameters': '600M'
        }
    }

    @classmethod
    def get_model_info(cls, model_key: str) -> Dict[str, Any]:
        """Get model configuration"""
        if model_key not in cls.MODELS:
            raise ValueError(f"Unknown model: {model_key}. Available: {list(cls.MODELS.keys())}")
        return cls.MODELS[model_key]

    @classmethod
    def list_models(cls) -> list:
        """List all available models"""
        return list(cls.MODELS.keys())

def load_model_and_tokenizer(model_key: str, device: torch.device) -> Tuple[Any, Any]:
    """
    Load protein foundation model and tokenizer.

    Args:
        model_key: Model identifier (e.g., 'esm2_650m')
        device: PyTorch device to load model on

    Returns:
        Tuple of (model, tokenizer)
    """
    model_info = ModelRegistry.get_model_info(model_key)

    try:
        # Load tokenizer
        tokenizer = model_info['tokenizer_class'].from_pretrained(model_info['name'])

        # Load model
        model = model_info['model_class'].from_pretrained(model_info['name'])
        model = model.to(device)
        model.eval()

        logger.info(f"Loaded {model_key} on {device}")
        logger.info(f"VRAM usage: {torch.cuda.memory_allocated()/1e9:.2f} GB")

        return model, tokenizer

    except Exception as e:
        logger.error(f"Failed to load {model_key}: {e}")

        # Fallback to ESM-2 650M if ESM-C not available
        if model_key.startswith('esmc_'):
            logger.warning(f"ESM-C not available, falling back to ESM-2 650M")
            return load_model_and_tokenizer('esm2_650m', device)

        raise

def get_model_architecture(model_key: str) -> str:
    """Get model architecture family"""
    return ModelRegistry.get_model_info(model_key)['architecture']

def get_model_parameters(model_key: str) -> str:
    """Get model parameter count"""
    return ModelRegistry.get_model_info(model_key)['parameters']