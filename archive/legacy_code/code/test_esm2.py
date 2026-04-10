import torch
from transformers import EsmForMaskedLM, EsmTokenizer
import time

def test_esm2():
    print("Loading ESM-2 650M...")
    model_name = "facebook/esm2_t33_650M_UR50D"
    tokenizer = EsmTokenizer.from_pretrained(model_name)
    model = EsmForMaskedLM.from_pretrained(model_name)
    device = torch.device("cuda")
    model = model.to(device)
    model.eval()
    print("Model loaded on", device)
    print("VRAM usage:", torch.cuda.memory_allocated()/1e9, "GB")
    print("ESM-2 test successful!")

if __name__ == "__main__":
    test_esm2()
