import subprocess


def main():
    subprocess.run([
        "python3", "-m", "grpc_tools.protoc",
        "-I.",
        "--python_out=src/generated",
        "--pyi_out=src/generated",
        "--grpc_python_out=src/generated",
        "proto/cloudberry_storage.proto"
    ], check=True)


if __name__ == "__main__":
    main()
