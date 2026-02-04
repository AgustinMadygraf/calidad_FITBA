import os
import subprocess
from dotenv import load_dotenv


def main() -> int:
    load_dotenv()
    domain = os.getenv("NGROK_URL")
    if not domain:
        print("NGROK_URL no configurada en .env")
        return 1

    cmd = ["ngrok", "http", "8000", f"--domain={domain}"]
    print("Ejecutando:", " ".join(cmd))
    return subprocess.call(cmd)


if __name__ == "__main__":
    raise SystemExit(main())
