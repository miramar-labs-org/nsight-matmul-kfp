"""
Nsight Operator validation pipeline.

Runs 20 iterations of an 8192x8192 CUDA matmul with NVTX annotations.
The component is labeled nvidia-nsight-profile=enabled so the Nsight
Operator injector webhook attaches nsys at pod creation — no nsys code
needed here.
"""

from kfp import dsl
from kfp import kubernetes


@dsl.component(
    base_image="nvcr.io/nvidia/pytorch:26.04-py3",
    packages_to_install=["nvtx"],
)
def cuda_matmul():
    import torch
    import nvtx

    x = torch.randn((8192, 8192), device="cuda")

    with nvtx.annotate("warmup", color="blue"):
        _ = x @ x
        torch.cuda.synchronize()

    with nvtx.annotate("bench", color="green"):
        for _ in range(20):
            z = x @ x
        torch.cuda.synchronize()

    print(f"Result norm: {z.norm().item():.4f}")


@dsl.pipeline(name="nsight-matmul-kfp")
def pipeline(run_id: str = "run-001"):
    task = cuda_matmul()
    task.set_gpu_limit(1).set_memory_limit("16G")
    kubernetes.add_pod_label(task, label_key="nvidia-nsight-profile", label_value="enabled")
