import itertools
import os
import string
import time
import sys

# ===== Settings =====
SUFFIX_ALPHABET = string.digits + "!@#$*/"
MAX_FILE_SIZE = 500 * 1024 * 1024  # 500 MB
SAFE_COMBO_WARNING = 10_000_000    # warn if total combos exceed this number

def case_variants(word: str):
    """Yield all case variants for a given word (letters toggle case, non-letters unchanged)."""
    pools = []
    for ch in word:
        if ch.isalpha():
            pools.append((ch.lower(), ch.upper()))
        else:
            pools.append((ch,))
    for combo in itertools.product(*pools):
        yield "".join(combo)

def suffixes_up_to(max_extra: int):
    """Yield all suffixes of length 0..max_extra using SUFFIX_ALPHABET (generator)."""
    for k in range(0, max_extra + 1):
        if k == 0:
            yield ""
        else:
            for tup in itertools.product(SUFFIX_ALPHABET, repeat=k):
                yield "".join(tup)

def count_stats(word: str, MAX_LEN: int):
    """Return (num_variants, estimated_bytes) for a single base word."""
    alpha_count = sum(ch.isalpha() for ch in word)
    base_variants = 1 << alpha_count  # 2^alpha_count
    max_extra = max(0, MAX_LEN - len(word))
    A = len(SUFFIX_ALPHABET)
    # total suffix combinations = sum_{k=0..max_extra} A^k
    total_suffixes = sum(A**k for k in range(max_extra + 1))
    num_variants = base_variants * total_suffixes
    # estimate bytes: base_variants * sum( (len(word)+k + newline) * A^k )
    estimated_bytes = base_variants * sum((len(word) + k + 1) * (A**k) for k in range(max_extra + 1))
    return num_variants, estimated_bytes

def generate_and_write(words, MAX_LEN, out_base="passwords"):
    """Generate combos and write into split files (<= MAX_FILE_SIZE)."""
    start_time = time.time()
    file_index = 1
    written_bytes = 0
    processed_lines = 0

    # compute total lines (may be large)
    total_lines = sum(count_stats(word, MAX_LEN)[0] for word in words)

    progress_interval = 10_000 if total_lines <= 1_000_000 else max(50_000, total_lines // 200)  # ~200 updates

    # open first file
    current_file = open(f"{out_base}_{file_index}.txt", "w", encoding="utf-8", newline="\n")

    try:
        for word in words:
            max_extra = max(0, MAX_LEN - len(word))
            for base in case_variants(word):
                for suf in suffixes_up_to(max_extra):
                    line = base + suf + "\n"
                    encoded = line.encode("utf-8")
                    line_size = len(encoded)

                    # split file if adding this line would exceed the per-file max
                    if written_bytes + line_size > MAX_FILE_SIZE:
                        current_file.close()
                        file_index += 1
                        written_bytes = 0
                        current_file = open(f"{out_base}_{file_index}.txt", "w", encoding="utf-8", newline="\n")

                    current_file.write(line)
                    written_bytes += line_size
                    processed_lines += 1

                    if processed_lines % progress_interval == 0:
                        elapsed = time.time() - start_time
                        # safe ETA calculation
                        if processed_lines > 0 and total_lines > 0:
                            remaining = (elapsed / processed_lines) * (total_lines - processed_lines)
                            eta_str = f" | ETA: {remaining:.1f}s"
                        else:
                            eta_str = ""
                        print(f"Progress: {processed_lines:,}/{total_lines:,} lines | Elapsed: {elapsed:.1f}s{eta_str}", end='\r')
    except KeyboardInterrupt:
        print("\nInterrupted by user. Flushing and closing files...")
    finally:
        try:
            current_file.close()
        except Exception:
            pass

    print()  # newline after progress line
    return file_index, processed_lines, time.time() - start_time

def main():
    # get max length (allow default if user presses enter)
    try:
        max_len_input = input("Enter maximum password length (default 12): ").strip()
        MAX_LEN = int(max_len_input) if max_len_input else 12
        if MAX_LEN <= 0:
            print("❌ Max length must be a positive integer.")
            return
    except ValueError:
        print("❌ Invalid input for max length.")
        return

    # get base words
    user_input = input("Enter base strings separated by commas (e.g., akshay,hello): ").strip()
    words = [w.strip() for w in user_input.split(",") if w.strip()]
    if not words:
        print("No valid input provided.")
        return

    # show lengths and validate against MAX_LEN
    print("\n=== String Lengths ===")
    validated = []
    for w in words:
        print(f"'{w}' → length {len(w)}")
        if len(w) > MAX_LEN:
            print(f"  ⚠️ Skipping '{w}' because its length ({len(w)}) > MAX_LEN ({MAX_LEN}).")
        else:
            validated.append(w)

    if not validated:
        print("No words to process after validation. Exiting.")
        return

    words = validated

    # preview counts and total size
    total_count = 0
    total_bytes = 0
    print("\n=== Preview ===")
    for w in words:
        count, bytes_ = count_stats(w, MAX_LEN)
        total_count += count
        total_bytes += bytes_
        print(f"'{w}': {count:,} combos, ~{bytes_ / (1024**3):.4f} GB")

    print(f"\nTOTAL: {total_count:,} combos, ~{total_bytes / (1024**3):.4f} GB\n")

    # warn for huge totals
    if total_count > SAFE_COMBO_WARNING:
        print(f"⚠️ WARNING: The total number of combos ({total_count:,}) is very large and may take a very long time to generate.")
        confirm = input("Type 'YES' (all caps) to proceed anyway: ").strip()
        if confirm != "YES":
            print("Cancelled by user.")
            return

    proceed = input("Proceed to generate and save to file(s)? (y/n): ").strip().lower()
    if proceed != "y":
        print("Cancelled. No file written.")
        return

    start = time.time()
    file_count, lines_written, elapsed = generate_and_write(words, MAX_LEN)
    print(f"\n✅ Generated (attempted) {lines_written:,} passwords")
    print(f"💾 Output split across {file_count} file(s), each ≤ {MAX_FILE_SIZE // (1024*1024)} MB")
    print(f"⏱ Total time: {elapsed:.1f}s")
    print("📂 Files named like: passwords_1.txt, passwords_2.txt, ...")

if __name__ == "__main__":
    main()