# CLAUDE.md

## What this repo is

nsight-matmul-kfp — a Kubeflow Pipelines project on the Miramar platform (DGX Spark).

<!-- Replace the line above with a one-sentence description. -->

## Key files

| File | Purpose |
|---|---|
| `pipeline.py` | KFP v2 pipeline definition — `pipeline()` is compiled and submitted |
| `notebook.ipynb` | Interactive development: compile, inspect, submit, monitor runs |
| `scripts/deploy_pipeline.py` | Compile + submit a run |
| `scripts/terminate_pipeline.py` | Called by Undeploy from KFP workflow |
| `scripts/purge_kfp.py` | Purge all runs + pipeline versions before redeploy |

## Slash commands

| Command | What it does |
|---|---|
| `/kfp-monitor [run-NNN]` | Self-paced monitoring loop — checks pods, appends to `runs/run-NNN.md` |
| `/nsight-interpret [run-NNN\|path]` | Interpret an Nsight Systems `.nsys-rep` with an LLM |

## Workflows

Require KFP running on DGX (`kubeflow` namespace). Trigger **Kubeflow Deploy** in
[miramar-platform-gcp](https://github.com/miramar-labs-org/miramar-platform-gcp) first.

| Workflow | Input | Effect |
|---|---|---|
| **Deploy to KFP** | `run_name` | Compile `pipeline.py` → upload → submit run |
| **Undeploy from KFP** | `run_id` | Terminate a run |

## Deploy cycle

```bash
# Always purge before redeploy
python3 scripts/purge_kfp.py

# Normal run
python3 scripts/deploy_pipeline.py --run-name run-001
```

## Editing the pipeline

`pipeline.py` defines the `cuda_matmul` component and wires it into the pipeline. To profile with
the Nsight Operator, add a pod label to the task (already in `pipeline.py`):

```python
from kfp import kubernetes
kubernetes.add_pod_label(task, label_key="nvidia-nsight-profile", label_value="enabled")
```

Compile check:

```sh
python3 -c "from kfp import compiler; from pipeline import pipeline; compiler.Compiler().compile(pipeline, '/tmp/p.yaml'); print('OK')"
```

## KFP UI access

```sh
ssh -L 8080:localhost:8080 <user>@spark-79b7.local
# http://localhost:8080
```

## Platform repo

[miramar-labs-org/miramar-platform-gcp](https://github.com/miramar-labs-org/miramar-platform-gcp)
