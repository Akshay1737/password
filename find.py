import os
import time

def search_in_files(base_filename, query):
    """Search query in multiple split files like base_filename_1.txt, base_filename_2.txt, ..."""
    file_index = 1
    found = False
    total_files = 0

    # Count total split files first
    while os.path.exists(f"{base_filename}_{file_index}.txt"):
        total_files += 1
        file_index += 1
    if total_files == 0:
        print(f"❌ No files found matching '{base_filename}_*.txt'")
        return None, None

    start_time = time.time()
    file_index = 1

    while file_index <= total_files:
        filename = f"{base_filename}_{file_index}.txt"
        print(f"🔍 Checking file: {filename}")
        try:
            with open(filename, "r", encoding="utf-8") as f:
                lines_checked = 0
                for line in f:
                    lines_checked += 1
                    if line.strip() == query:  # exact match
                        elapsed = time.time() - start_time
                        print(f"\n⏱ Time elapsed: {elapsed:.2f}s")
                        return True, filename
                    if lines_checked % 10000 == 0:  # progress update
                        elapsed = time.time() - start_time
                        remaining_files = total_files - file_index
                        est_remaining = (elapsed / file_index) * remaining_files
                        print(f"Progress: File {file_index}/{total_files} | "
                              f"Elapsed: {elapsed:.2f}s | Est. remaining: {est_remaining:.2f}s", end='\r')
        except Exception as e:
            print(f"❌ Error reading '{filename}': {e}")
            return None, None

        file_index += 1

    elapsed = time.time() - start_time
    print(f"\n⏱ Total time: {elapsed:.2f}s")
    return False, None

def main():
    base_filename = "passwords"  # base name used in split files
    query = input("Enter string to search: ").strip()

    found, filename = search_in_files(base_filename, query)

    if found:
        print(f"✅ '{query}' found in '{filename}'")
    else:
        print(f"❌ '{query}' NOT found in any file matching '{base_filename}_*.txt'")

if __name__ == "__main__":
    main()
