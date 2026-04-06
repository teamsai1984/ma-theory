"""
Ma Theory — Weight Interpolation Track (Negative Control)
=========================================================
Pythia-410m + LoRA weight interpolation.

Base: EleutherAI/pythia-410m
LoRA: rank=64, alpha=256, target=qkv, trained on code_search_net/python
Interpolation: λ = 0.0 to 1.0 (16 points)
Eval: WikiText-2 test, 50 samples × 3 seeds
"""

import torch
import torch.nn.functional as F
from transformers import AutoModelForCausalLM, AutoTokenizer
from datasets import load_dataset
from peft import LoraConfig, get_peft_model, PeftModel
import numpy as np
import random
import json
import argparse
import copy
from pathlib import Path

MODEL_NAME = "EleutherAI/pythia-410m"
NUM_SAMPLES = 50
MAX_LENGTH = 512
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# LoRA training config
LORA_CONFIG = LoraConfig(
    r=64, lora_alpha=256,
    target_modules=["query_key_value"],
    lora_dropout=0.0, bias="none",
    task_type="CAUSAL_LM",
)
TRAIN_DATASET = "code_search_net"
TRAIN_SUBSET = "python"
TRAIN_SAMPLES = 5000
TRAIN_LR = 1e-4
TRAIN_STEPS = 10000

LAMBDA_VALUES = [0.0, 0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35,
                 0.4, 0.45, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]


def set_seed(seed):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def load_eval_data(tokenizer, seed):
    set_seed(seed)
    dataset = load_dataset("wikitext", "wikitext-2-raw-v1", split="test")
    full_text = "\n".join([t for t in dataset["text"] if len(t.strip()) > 0])
    full_tokens = tokenizer.encode(full_text, return_tensors="pt")[0]
    max_start = len(full_tokens) - MAX_LENGTH - 1
    starts = np.random.randint(0, max_start, size=NUM_SAMPLES)
    return [full_tokens[s:s + MAX_LENGTH].unsqueeze(0).to(DEVICE) for s in starts]


def train_lora(base_model, tokenizer):
    """Train LoRA adapter. Returns delta_W dict."""
    print("Training LoRA adapter...")
    from datasets import load_dataset as ld
    train_data = ld(TRAIN_DATASET, TRAIN_SUBSET, split="train")
    train_texts = [s["whole_func_string"] for s in train_data.select(range(TRAIN_SAMPLES))]

    model = get_peft_model(copy.deepcopy(base_model), LORA_CONFIG).to(DEVICE)
    model.train()
    optimizer = torch.optim.AdamW(model.parameters(), lr=TRAIN_LR)

    for step in range(TRAIN_STEPS):
        text = train_texts[step % len(train_texts)]
        inputs = tokenizer(text, return_tensors="pt", truncation=True,
                          max_length=MAX_LENGTH).to(DEVICE)
        outputs = model(**inputs, labels=inputs["input_ids"])
        loss = outputs.loss
        loss.backward()
        optimizer.step()
        optimizer.zero_grad()
        if (step + 1) % 1000 == 0:
            print(f"  Step {step+1}/{TRAIN_STEPS}, Loss: {loss.item():.4f}")

    # Extract LoRA delta weights
    delta_w = {}
    for name, param in model.named_parameters():
        if "lora_" in name:
            delta_w[name] = param.data.clone().cpu()

    del model
    torch.cuda.empty_cache()
    return delta_w


def interpolate_model(base_model, delta_w, lam):
    """Create interpolated model: W(λ) = W_base + λ * ΔW"""
    model = copy.deepcopy(base_model)
    peft_model = get_peft_model(model, LORA_CONFIG).to(DEVICE)

    with torch.no_grad():
        for name, param in peft_model.named_parameters():
            if name in delta_w:
                param.copy_(delta_w[name].to(DEVICE) * lam)

    peft_model.eval()
    return peft_model


@torch.no_grad()
def measure_sample(teacher, student, input_ids):
    t_out = teacher(input_ids, output_hidden_states=True)
    s_out = student(input_ids, output_hidden_states=True)
    t_logits = t_out.logits.float()
    s_logits = s_out.logits.float()

    t_logp = F.log_softmax(t_logits, dim=-1)
    s_logp = F.log_softmax(s_logits, dim=-1)
    t_p = t_logp.exp()
    eps_star = (t_p * (t_logp - s_logp)).sum(dim=-1).sum().item()

    t_pred = t_logits.argmax(dim=-1)
    s_pred = s_logits.argmax(dim=-1)
    p_agree = (t_pred == s_pred).float().mean().item()

    t_hidden = t_out.hidden_states[-1].float()
    s_hidden = s_out.hidden_states[-1].float()
    t_phi = F.normalize(t_hidden.mean(dim=1), dim=-1)
    s_phi = F.normalize(s_hidden.mean(dim=1), dim=-1)
    d_nov = 1.0 - (t_phi * s_phi).sum().item()

    return eps_star, d_nov, p_agree, d_nov * p_agree


def run_experiment(seed, output_dir):
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    tokenizer.pad_token = tokenizer.eos_token
    samples = load_eval_data(tokenizer, seed)

    base_model = AutoModelForCausalLM.from_pretrained(
        MODEL_NAME, torch_dtype=torch.float16
    ).to(DEVICE).eval()

    # Train LoRA (or load cached)
    delta_w = train_lora(base_model, tokenizer)

    # Teacher = base model (λ=0)
    teacher = base_model
    results = []

    for lam in LAMBDA_VALUES:
        print(f"[Seed {seed}] λ={lam}...")
        student = interpolate_model(base_model, delta_w, lam)

        metrics = []
        for i, inp in enumerate(samples):
            eps, dnov, pagree, eagree = measure_sample(teacher, student, inp)
            metrics.append({"eps_star": eps, "d_nov": dnov,
                           "p_agree": pagree, "e_agree": eagree})

        eps_vals = [m["eps_star"] for m in metrics]
        result = {
            "lambda": lam, "seed": seed,
            "eps_mean": np.mean(eps_vals),
            "eps_se": np.std(eps_vals) / np.sqrt(NUM_SAMPLES),
            "dnov_mean": np.mean([m["d_nov"] for m in metrics]),
            "pagree_mean": np.mean([m["p_agree"] for m in metrics]),
            "eagree_mean": np.mean([m["e_agree"] for m in metrics]),
        }
        results.append(result)
        print(f"  ε*={result['eps_mean']:.2f}, E_agree={result['eagree_mean']:.4f}")
        del student
        torch.cuda.empty_cache()

    out_file = output_dir / f"results_interp_seed{seed}.json"
    with open(out_file, "w") as f:
        json.dump(results, f, indent=2)
    print(f"Saved: {out_file}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--output_dir", type=str, default="results_interp")
    args = parser.parse_args()
    run_experiment(args.seed, args.output_dir)
