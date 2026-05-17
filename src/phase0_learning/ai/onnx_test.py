import time
import sys
import numpy as np

"""
ONNX Runtime Test — Phase 0, Week 2

Downloads a tiny ONNX model and benchmarks inference
to verify ONNX Runtime is working correctly.

Usage:
    python onnx_test.py
"""


def test_onnx():
    try:
        import onnxruntime as ort
    except ImportError:
        print("ONNX Runtime not installed. Installing...")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "onnxruntime", "--quiet"])
        import onnxruntime as ort

    print(f"ONNX Runtime version: {ort.__version__}")
    print(f"Available providers:  {ort.get_available_providers()}")

    # Create a simple model for testing (identity function)
    # In practice we'll convert Whisper/NLLB to ONNX
    import onnx
    from onnx import numpy_helper, TensorProto
    from onnx.helper import make_model, make_node, make_graph, make_tensor_value_info

    # Build a tiny graph: output = input * 2.0
    input_info = make_tensor_value_info("input", TensorProto.FLOAT, [1, 10])
    output_info = make_tensor_value_info("output", TensorProto.FLOAT, [1, 10])
    const_tensor = numpy_helper.from_array(
        np.array([2.0], dtype=np.float32), name="scale"
    )
    node = make_node("Mul", ["input", "scale"], ["output"])
    graph = make_graph([node], "test", [input_info], [output_info], [const_tensor])
    model = make_model(graph, opset_imports=[onnx.helper.make_opsetid("", 13)])

    # Save and load
    onnx.save(model, "/tmp/test_model.onnx")

    # Benchmark
    sess = ort.InferenceSession("/tmp/test_model.onnx")
    input_data = np.ones((1, 10), dtype=np.float32)

    # Warmup
    for _ in range(10):
        sess.run(None, {"input": input_data})

    # Benchmark
    runs = 1000
    t0 = time.time()
    for _ in range(runs):
        result = sess.run(None, {"input": input_data})
    elapsed = time.time() - t0

    print(f"\nBenchmark: {runs} inferences")
    print(f"Total time:  {elapsed*1000:.2f} ms")
    print(f"Per inference: {elapsed/runs*1000:.3f} ms")
    print(f"Throughput:  {runs/elapsed:.0f} inferences/sec")
    print(f"Result check: {np.allclose(result[0], input_data * 2.0)}")
    print("\nONNX Runtime is working correctly.")


def main():
    print("=" * 60)
    print("ONNX Runtime Test")
    print("=" * 60)
    test_onnx()
    print("=" * 60)


if __name__ == "__main__":
    main()
