import subprocess


def main():
    subprocess.run([
        "python3", "-m", "grpc_tools.protoc",
        "-I.",
        "--python_out=src/generated",
        "--pyi_out=src/generated",
        "--grpc_python_out=src/generated",
        "cloudberry_storage.proto"
    ], check=True)

    subprocess.run([
        "python3", "-m", "grpc_tools.protoc",
        "-I.",
        "--python_out=src/generated",
        "--pyi_out=src/generated",
        "--grpc_python_out=src/generated",
        "one_peace_service.proto"
    ], check=True)


if __name__ == "__main__":
    main()
