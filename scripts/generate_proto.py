import subprocess


def main():
    subprocess.run([
        "python3", "-m", "grpc_tools.protoc",
        "-I.",
        "--python_out=src",
        "--pyi_out=src",
        "--grpc_python_out=src",
        "cloudberry_storage.proto"
    ], check=True)

    subprocess.run([
        "python3", "-m", "grpc_tools.protoc",
        "-I.",
        "--python_out=src",
        "--pyi_out=src",
        "--grpc_python_out=src",
        "one_peace_service.proto"
    ], check=True)


if __name__ == "__main__":
    main()
