import os

def split_jsonl_file(file_path):
    # Determine output file names
    base_name, ext = os.path.splitext(file_path)
    part1_name = f"{base_name}_part1{ext}"
    part2_name = f"{base_name}_part2{ext}"
    
    # Count total lines
    with open(file_path, 'r', encoding='utf-8') as file:
        total_lines = sum(1 for _ in file)
    
    print(f"Total lines in file: {total_lines}")
    
    # Split point (half of the lines)
    split_point = total_lines // 2
    
    # Write to two files
    with open(file_path, 'r', encoding='utf-8') as infile, \
         open(part1_name, 'w', encoding='utf-8') as part1, \
         open(part2_name, 'w', encoding='utf-8') as part2:
        
        for i, line in enumerate(infile):
            if i < split_point:
                part1.write(line)
            else:
                part2.write(line)
    
    print(f"File successfully split into '{part1_name}' and '{part2_name}'.")

USERNAME = "panchojasen"
LARGE_JSON_FILE = (
    f"/home/{USERNAME}/Projects/diariodeleon-scraper/results/embeddings/resultados_antiguos_embeddings.jsonl"
)


# Example usage
split_jsonl_file(LARGE_JSON_FILE)