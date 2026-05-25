import itertools
import string
import time

# ===== Settings =====
SUFFIX_ALPHABET = string.digits + "!@#$*/"
MAX_FILE_SIZE = 500 * 1024 * 1024  # 500 MB

def case_variants(word: str):
    """Yield all case variants for a given word."""
    pools = []
    for ch in word:
        if ch.isalpha():
            pools.append((ch.lower(), ch.upper()))
        else:
            pools.append((ch,))
    for combo in itertools.product(*pools):
        yield "".join(combo)

def suffixes_exact(length: int):
    """Yield all suffixes of exactly `length` using SUFFIX_ALPHABET."""
    if length == 0:
        yield ""
    else:
        for tup in itertools.product(SUFFIX_ALPHABET, repeat=length):
            yield "".join(tup)

def generate_and_write(words, target_lengths, out_base="passwords_len11_12"):
    """Generate only passwords of given target lengths."""
    start_time = time.time()
    file_index = 1
    written_bytes = 0
    processed_lines = 0

    current_file = open(f"{out_base}_{file_index}.txt", "w", encoding="utf-8", newline="\n")

    try:
        for word in words:
            for base in case_variants(word):
                for target_len in target_lengths:
                    extra = target_len - len(base)
                    if extra < 0:
                        continue
                    for suf in suffixes_exact(extra):
                        line = base + suf + "\n"
                        encoded = line.encode("utf-8")
                        line_size = len(encoded)

                        # Split into new file if exceeding max size
                        if written_bytes + line_size > MAX_FILE_SIZE:
                            current_file.close()
                            file_index += 1
                            written_bytes = 0
                            current_file = open(f"{out_base}_{file_index}.txt", "w", encoding="utf-8", newline="\n")

                        current_file.write(line)
                        written_bytes += line_size
                        processed_lines += 1

                        if processed_lines % 100000 == 0:
                            elapsed = time.time() - start_time
                            print(f"Progress: {processed_lines:,} lines | Elapsed: {elapsed:.1f}s", end='\r')
    finally:
        current_file.close()

    print(f"\n✅ Generated {processed_lines:,} passwords")
    print(f"💾 Output split across {file_index} file(s), each ≤ {MAX_FILE_SIZE // (1024*1024)} MB")
    print(f"⏱ Total time: {time.time() - start_time:.1f}s")
    print("📂 Files named like: passwords_len11_12_1.txt, passwords_len11_12_2.txt, ...")

def main():
    # get base words
    user_input = input("Enter base strings separated by commas: ").strip()
    words = [w.strip() for w in user_input.split(",") if w.strip()]
    if not words:
        print("No valid words.")
        return

    print("\n=== Target: ONLY passwords of length 11 and 12 ===")
    generate_and_write(words, target_lengths=[11, 12])

if __name__ == "__main__":
    main()
