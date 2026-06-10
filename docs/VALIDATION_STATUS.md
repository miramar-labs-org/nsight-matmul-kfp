# Validation Status — nsight-matmul-kfp

**Model/Task:** CUDA matmul benchmark — Nsight Operator profiling of a KFP GPU component on DGX Spark
**Platform:** Kubeflow Pipelines on NVIDIA DGX Spark (GB10, 128 GB unified memory)
**Last updated:** 2026-06-10

---

## Current Status

| Component | Status |
|---|---|
| `cuda_matmul` | ✅ Completed (run-009 onward) |
| GPU profiling (Nsight Operator) | ✅ Working — run-009 first full CUDA kernel capture |

**run-011 completed.** Full CUDA kernel data captured via Nsight Operator pod-label injection.

---

## Run Table

| Run | Purpose | Result | Key Finding |
|---|---|---|---|
| run-001 | Validate pod-label approach | ✅ Operator injects nsys | Namespace label caused DAG driver pod failure; per-pod label is correct |
| run-002 | First operator capture | ✅ `.nsys-rep` generated | Empty GPU events — CUPTI access issue |
| run-003–004 | CUPTI access fix | ✅ Partial | Hardware trace binary section present but no kernel table in SQL |
| run-005 | Privileged injector | ✅ | `privileged: true` in Helm values required for hw perf counters |
| run-006 | GPU device visibility | ✅ | `NVIDIA_VISIBLE_DEVICES=all` in nsightToolArgs |
| run-007–008 | Collection timing | ✅ | Pre-arm via coordinator REST API prevents early-stop issue |
| run-009 | First full CUDA capture | ✅ GREEN | 47 KERNEL rows in SQL; 728K `.nsys-rep` with matmul data |
| run-010 | Pod targeting race fix | ✅ | Added pod suffix exclusion to coordinator script |
| run-011 | Subprocess env isolation | ✅ | `libNsightProcessHook.so` env inheritance verified |

> Update this table after each run.

---

## What Is Implemented

### Infrastructure (inherited from platform template)
- KFP v2 pipeline with GPU component using NGC PyTorch base image
- Nsight Operator pod-label profiling: `kubernetes.add_pod_label(task, "nvidia-nsight-profile", "enabled")`
- `purge_kfp_mlflow.py`, `purge_nsight.py`
- `deploy_pipeline.py` with `--run-name`

### Project-specific
- `pipeline.py` — `cuda_matmul` component performing FP32/FP16/BF16 matmul benchmarks
- Nsight Operator Helm values with `privileged: true` and `NVIDIA_VISIBLE_DEVICES=all`
- Pre-arm coordinator script in `scripts/`

---

## What Is Still Pending

- Blog post / write-up of Nsight Operator end-to-end workflow

---

## Known Issues

None active.

---

## Fixed Issues

### Namespace label injects nsys into DAG driver pods → `runAsNonRoot` failure (run-001)
Do NOT label the `kubeflow` namespace with `nvidia-nsight-profile=enabled`. Use per-pod
`kubernetes.add_pod_label(task, "nvidia-nsight-profile", "enabled")` only.

### Empty CUDA trace — `RmProfilingAdminOnly=1` (run-002 through run-004)
NVIDIA driver defaults restrict CUPTI to root. Fix: `/etc/modprobe.d/nvidia.conf` with
`options nvidia NVreg_RestrictProfilingToAdminUsers=0`, then reboot DGX.

### Nsight Operator requires `privileged: true` in Helm values (run-005)
Hardware GPU performance counters (used by `cuda_gpu_kern_sum`) require privileged mode in the
injector container. Added to `dgx/minikube/nsight/values.yaml`.

---

## Latest Profiling Finding

See [runs/run-009/analysis-ollama-qwen3-coder-30b.md](../runs/run-009/analysis-ollama-qwen3-coder-30b.md) for the most recent `/nsight-interpret` analysis.
