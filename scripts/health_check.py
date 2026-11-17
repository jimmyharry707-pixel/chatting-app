"""Small command-line health check for a running messenger API."""
import argparse,requests,sys

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--url",default="http://127.0.0.1:8000")
    args=parser.parse_args()
    try:
        response=requests.get(args.url.rstrip("/")+"/health",timeout=5)
        response.raise_for_status()
        print(response.json())
    except requests.RequestException as exc:
        print(f"Health check failed: {exc}",file=sys.stderr)
        raise SystemExit(1)
if __name__=="__main__": main()
