"""
Ma Theory — Pythia-410m Distillation Track Experiment
=====================================================
Google Colab (T4/A100) compatible.

Teacher: EleutherAI/pythia-410m step=143000
Students: steps 0, 1000, 2000, 4000, 8000, 16000, 32000, 64000, 128000
Eval: WikiText-2 test, 50 samples × 3 seeds
"""

import torch
import torch.nn.functional as F
from transformers import AutoModelForCausalLM, AutoTokenizer
from datasets import load_dataset
import numpy as np
import random
import json
import csv
import argparse
from pathlib import Path

MODEL_NAME = "EleutherAI/pythia-410m"
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
    """Load WikiText-2 test and sample NUM_SAMPLES sequences."""
    set_seed(seed)
    dataset = load_dataset("wikitext", "wikitext-2-raw-v1", split="test")
    full_text = "\n".join([t for t in dataset["text"] if len(t.strip()) > 0])
    full_tokens = tokenizer.encode(full_text, return_tensors="pt")[0]

    max_start = len(full_tokens) - MAX_LENGTH - 1
    starts = np.random.randint(0, max_start, size=NUM_SAMPLES)
    samples = [full_tokens[s:s + MAX_LENGTH].unsqueeze(0).to(DEVICE) for s in starts]
    return samples


def load_model(revision):
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_NAME, revision=revision, torch_dtype=torch.float16
    ).to(DEVICE).eval()
    return model


@torch.no_grad()
def measure_sample(teacher, student, input_ids):
    """Measure ε*, D_nov, P_agree, E_agree for a single sample."""
    T = input_ids.shape[1]

    # Forward pass (float32 for KL precision)
    t_out = teacher(input_ids, output_hidden_states=True)
    s_out = student(input_ids, output_hidden_states=True)

    t_logits = t_out.logits.float()
    s_logits = s_out.logits.float()

    # ε* = sum_t KL(p_T || p_S)
    t_logp = F.log_softmax(t_logits, dim=-1)
    s_logp = F.log_softmax(s_logits, dim=-1)
    t_p = t_logp.exp()
    kl_per_token = (t_p * (t_logp - s_logp)).sum(dim=-1)  # [1, T]
    eps_star = kl_per_token.sum().item()

    # P_agree = fraction of tokens where argmax matches
    t_pred = t_logits.argmax(dim=-1)  # [1, T]
    s_pred = s_logits.argmax(dim=-1)
    p_agree = (t_pred == s_pred).float().mean().item()

    # D_nov = 1 - cos(phi_T, phi_S)
    t_hidden = t_out.hidden_states[-1].float()  # [1, T, D]
    s_hidden = s_out.hidden_states[-1].float()
    t_phi = F.normalize(t_hidden.mean(dim=1), dim=-1)  # [1, D]
    s_phi = F.normalize(s_hidden.mean(dim=1), dim=-1)
    d_nov = 1.0 - (t_phi * s_phi).sum().item()

    e_agree = d_nov * p_agree
    return eps_star, d_nov, p_agree, e_agree


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
            step_metrics.append({
                "sample": i, "eps_star": eps, "d_nov": dnov,
                "p_agree": pagree, "e_agree": eagree
            })

        # Aggregate
        eps_vals = [m["eps_star"] for m in step_metrics]
        dnov_vals = [m["d_nov"] for m in step_metrics]
        pagree_vals = [m["p_agree"] for m in step_metrics]
        eagree_vals = [m["e_agree"] for m in step_metrics]

        result = {
            "step": step, "seed": seed,
            "eps_mean": np.mean(eps_vals), "eps_se": np.std(eps_vals) / np.sqrt(NUM_SAMPLES),
            "dnov_mean": np.mean(dnov_vals), "pagree_mean": np.mean(pagree_vals),
            "eagree_mean": np.mean(eagree_vals),
        }
        results.append(result)
        print(f"  ε*={result['eps_mean']:.2f}±{result['eps_se']:.2f}, "
              f"D_nov={result['dnov_mean']:.4f}, P_agree={result['pagree_mean']:.4f}, "
              f"E_agree={result['eagree_mean']:.4f}")

        del student
        torch.cuda.empty_cache()

    del teacher
    torch.cuda.empty_cache()

    # Save
    out_file = output_dir / f"results_410m_seed{seed}.json"
    with open(out_file, "w") as f:
        json.dump(results, f, indent=2)
    print(f"Saved: {out_file}")
    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--output_dir", type=str, default="results_410m")
    args = parser.parse_args()
    run_experiment(args.seed, args.output_dir)
