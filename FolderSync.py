import os
import shutil
import hashlib
import time
import argparse
import logging

def calculate_md5(file_path):
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as file:
        # Reads pieces of data up to 4096 bytes until it finds an empty byte string represented as b""
        for data in iter(lambda: file.read(4096), b""):
            hash_md5.update(data)
    return hash_md5.hexdigest()

def sync_folders(source, replica, log_file):
    # Set up logging
    logging.basicConfig(filename=log_file, level=logging.INFO, format='%(asctime)s - %(message)s')

    source_files = {}
    replica_files = {}

    # Walk through the source folder and calculate file hashes
    for root, dirs, files in os.walk(source):
        for file in files:
            file_path = os.path.join(root, file)
            relative_path = os.path.relpath(file_path, source)
            source_files[relative_path] = calculate_md5(file_path)

    # Walk through the replica folder and calculate file hashes
    for root, dirs, files in os.walk(replica):
        for file in files:
            file_path = os.path.join(root, file)
            relative_path = os.path.relpath(file_path, replica)
            replica_files[relative_path] = calculate_md5(file_path)

    # Copy new and modified files from source to replica
    for relative_path, md5_hash in source_files.items():
        source_file = os.path.join(source, relative_path)
        replica_file = os.path.join(replica, relative_path)

        # If the path doesn't exist it copies the files
        if relative_path not in replica_files:
            os.makedirs(os.path.dirname(replica_file), exist_ok=True)
            shutil.copy2(source_file, replica_file)
            logging.info(f"Copied file: {source_file} to {replica_file}")
            print(f"Copied file: {source_file} to {replica_file}")
        # If the path exists and but de hash is diferent it updates the files
        elif replica_files[relative_path] != md5_hash:
            shutil.copy2(source_file, replica_file)
            logging.info(f"Updated file: {source_file} in {replica_file}")
            print(f"Updated file: {source_file} in {replica_file}")

    # Remove files from replica that are not in source
    for relative_path in replica_files.keys():
        if relative_path not in source_files:
            replica_file = os.path.join(replica, relative_path)
            os.remove(replica_file)
            logging.info(f"Deleted file: {replica_file}")
            print(f"Deleted file: {replica_file}")

def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Folder synchronization program.")
    parser.add_argument('source', help="Path to the source folder.")
    parser.add_argument('replica', help="Path to the replica folder.")
    parser.add_argument('interval', type=int, help="Synchronization interval in seconds.")
    parser.add_argument('log_file', help="Path to the log file.")

    args = parser.parse_args()

    source = args.source
    replica = args.replica
    interval = args.interval
    log_file = args.log_file

    while True:
        sync_folders(source, replica, log_file)
        time.sleep(interval)

if __name__ == "__main__":
    main()
