import re
import subprocess
import sys
import os

def run_shell_command(command):
    """
    Executa um comando de shell e captura a saída.
    """
    try:
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Erro ao executar comando: {e.cmd}")
        print(f"Erro: {e.stderr}")
        sys.exit(1)

def compile_c_code(c_file, output_file):
    """
    Compila um arquivo C para um executável.
    """
    if not os.path.exists(c_file):
        print(f"Erro: O arquivo C '{c_file}' não foi encontrado.")
        sys.exit(1)
    
    print("Compilando código C...")
    command = ["gcc", c_file, "-o", output_file]
    run_shell_command(command)

def run_valgrind(c_program, trace_file):
    """
    Executa o programa C com Valgrind para gerar o trace de memória.
    """
    print(f"Executando Valgrind para gerar trace de memória...")
    command = ["valgrind", "--log-file=" + trace_file, "--tool=lackey", "--trace-mem=yes", "./" + c_program]
    run_shell_command(command)

def process_trace(trace_file, page_size=4096):
    """
    Processa o arquivo de trace e gera a reference string separada entre instrução e dados.
    """
    if not os.path.exists(trace_file):
        print(f"Erro: O arquivo de trace '{trace_file}' não foi encontrado.")
        sys.exit(1)

    instruction_refs = []  # Lista para referências de instrução
    data_refs = []         # Lista para referências de dados
    page_mask = ~(page_size - 1)  # Máscara para pegar apenas os bits que representam a página

    with open(trace_file, 'r') as file:
        for line in file:
            line = line.strip().replace('\t', ' ')  # Limpeza de tabulações extras

            # Regex para capturar as linhas relevantes
            match = re.match(r"^[ILSM]\s+([0-9a-fA-Fx]+),\s*\d+", line)
            if match:
                address = int(match.group(1), 16)  # Converte o endereço para inteiro
                page_number = address & page_mask   # Calcula o número da página

                # Se for uma instrução
                if line[0] == 'I':
                    instruction_refs.append(f"{page_number:X}")  # Adiciona o número da página em hexadecimal
                # Se for um dado (acessos de 'S', 'L', 'M')
                elif line[0] in ['S', 'L', 'M']:
                    data_refs.append(f"{page_number:X}")  # Adiciona o número da página em hexadecimal

    return instruction_refs, data_refs

def save_reference_string(reference_string, filename):
    """
    Salva a reference string em um arquivo.
    """
    with open(filename, 'w') as file:
        file.write("\n".join(reference_string))

def run_simulator(reference_file, tlb_size):
    """
    Executa o simulador TLB com a reference string e o tamanho da TLB.
    """
    if not os.path.exists(reference_file):
        print(f"Erro: O arquivo '{reference_file}' não foi encontrado.")
        sys.exit(1)

    print(f"Executando o simulador TLB com tamanho {tlb_size}...")
    subprocess.run(["./TLB", reference_file, str(tlb_size)], check=True)

def main():
    if len(sys.argv) != 4:
        print("Uso: python3 script.py <c_file> <trace_file> <tlb_size>")
        sys.exit(1)

    c_file = sys.argv[1]
    trace_file = sys.argv[2]
    tlb_size = int(sys.argv[3])

    # Passos principais do script
    compile_c_code(c_file, "main")
    run_valgrind("main", trace_file)
    
    # Processa o trace e gera referências separadas para instrução e dados
    instruction_refs, data_refs = process_trace(trace_file)
    
    print(f"{len(instruction_refs)} páginas de instrução e {len(data_refs)} páginas de dados na reference string.")
    
    # Salva as referências separadas em arquivos distintos
    save_reference_string(instruction_refs, "instruction_reference_string.txt")
    save_reference_string(data_refs, "data_reference_string.txt")

    # Executa o simulador TLB para instrução
    print("\nSimulando TLB para instrução...")
    run_simulator("instruction_reference_string.txt", tlb_size)

    # Executa o simulador TLB para dados
    print("\nSimulando TLB para dados...")
    run_simulator("data_reference_string.txt", tlb_size)

if __name__ == "__main__":
    main()
