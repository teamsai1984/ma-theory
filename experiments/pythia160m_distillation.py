"""
Ma Theory — Pythia-160m Distillation Track Experiment
=====================================================
Google Colab (A100 recommended) compatible.

Teacher: EleutherAI/pythia-160m step=143000
Students: steps 0, 1000, 2000, 4000, 8000, 16000, 32000, 64000, 128000
Eval: WikiText-2 test, 50 samples × 3 seeds

Usage (Colab):
  Upload this file and run each seed:
    !python pythia160m_distillation.py --seed 42
    !python pythia160m_distillation.py --seed 123
    !python pythia160m_distillation.py --seed 456
"""

import torch
import torch.nn.functional as F
from transformers import AutoModelForCausalLM, AutoTokenizer
from datasets import load_dataset
import numpy as np
import random
import json
import argparse
from pathlib import Path

MODEL_NAME = "EleutherAI/pythia-160m"
TEACHER_REVISION = "step143000"
STUDENT_STEPS = [0, 1000, 2000, 4000, 8000, 16000, 32000, 64000, 128000]
NUM_SAMPLES = 50
MAX_LENGTH = 512
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")


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


def load_model(revision):
    return AutoModelForCausalLM.from_pretrained(
        MODEL_NAME, revision=revision, torch_dtype=torch.float16
    ).to(DEVICE).eval()


@torch.no_grad()
def measure_sample(teacher, student, input_ids):
    t_out = teacher(input_ids, output_hidden_states=True)
    s_out = student(input_ids, output_hidden_states=True)
    t_logits = t_out.logits.float()
    s_logits = s_out.logits.float()

    t_logp = F.log_softmax(t_logits, dim=-1)
    s_logp = F.log_softmax(s_logits, dim=-1)
    t_p = t_logp.exp()
    kl_per_token = (t_p * (t_logp - s_logp)).sum(dim=-1)
    eps_star = kl_per_token.sum().item()

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
    teacher = load_model(TEACHER_REVISION)
    results = []

    for step in STUDENT_STEPS:
        print(f"[Seed {seed}] Step {step}...")
        student = load_model(f"step{step}")
        step_metrics = []
        for i, inp in enumerate(samples):
            eps, dnov, pagree, eagree = measure_sample(teacher, student, inp)
            step_metrics.append({"sample": i, "eps_star": eps, "d_nov": dnov,
                                 "p_agree": pagree, "e_agree": eagree})

        eps_vals = [m["eps_star"] for m in step_metrics]
        result = {
            "step": step, "seed": seed,
            "eps_mean": np.mean(eps_vals),
            "eps_se": np.std(eps_vals) / np.sqrt(NUM_SAMPLES),
            "dnov_mean": np.mean([m["d_nov"] for m in step_metrics]),
            "pagree_mean": np.mean([m["p_agree"] for m in step_metrics]),
            "eagree_mean": np.mean([m["e_agree"] for m in step_metrics]),
        }
        results.append(result)
        print(f"  ε*={result['eps_mean']:.2f}, E_agree={result['eagree_mean']:.4f}")
        del student
        torch.cuda.empty_cache()

    del teacher
    torch.cuda.empty_cache()

    out_file = output_dir / f"results_160m_seed{seed}.json"
    with open(out_file, "w") as f:
        json.dump(results, f, indent=2)
    print(f"Saved: {out_file}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--output_dir", type=str, default="results_160m")
    args = parser.parse_args()
    run_experiment(args.seed, args.output_dir)
