"""Create a consistent SQLite backup using the online backup API."""
import argparse,sqlite3
from pathlib import Path
from server.config import settings

def backup(destination):
    destination=Path(destination); destination.parent.mkdir(parents=True,exist_ok=True)
    source=sqlite3.connect(str(settings.database_path))
    target=sqlite3.connect(str(destination))
    try: source.backup(target)
    finally: target.close(); source.close()
    return destination

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("destination",help="Path to the backup .db file")
    args=parser.parse_args()
    print(f"Database backup written to {backup(args.destination)}")
if __name__=="__main__": main()
