from sqlalchemy.orm import Session
from app.models import models
import re
import os
from typing import List
from elftools.elf.elffile import ELFFile
from elftools.elf.sections import SymbolTableSection
from capstone import Cs, CS_ARCH_X86, CS_MODE_64, CS_ARCH_ARM, CS_MODE_ARM
import hashlib

class AnalysisService:
    @staticmethod
    def scan_binary(db: Session, binary_id: int):
        """
        Scans all functions in a binary against vulnerability patterns.
        """
        binary = db.query(models.Binary).filter(models.Binary.id == binary_id).first()
        if not binary:
            return None

        patterns = db.query(models.Pattern).all()
        findings_created = 0

        for function in binary.functions:
            for pattern in patterns:
                # Basic regex matching on the assembly snippet
                if function.assembly_snippet and re.search(pattern.pattern, function.assembly_snippet, re.IGNORECASE):
                    # Check if finding already exists
                    existing = db.query(models.Finding).filter(
                        models.Finding.function_id == function.id,
                        models.Finding.pattern_id == pattern.id
                    ).first()

                    if not existing:
                        finding = models.Finding(
                            function_id=function.id,
                            pattern_id=pattern.id,
                            severity=pattern.severity,
                            confidence=pattern.confidence_base,
                            evidence=f"Match found for pattern '{pattern.name}' in function '{function.name}'",
                            recommendation=f"Review usage of dangerous pattern in {function.name}. Consider using safer alternatives."
                        )
                        db.add(finding)
                        findings_created += 1

        db.commit()
        return findings_created

    @staticmethod
    def analyze_elf(db: Session, binary_id: int, file_path: str):
        """
        Real ELF analysis using pyelftools and capstone.
        """
        binary = db.query(models.Binary).filter(models.Binary.id == binary_id).first()
        if not binary or not os.path.exists(file_path):
            return False

        try:
            with open(file_path, 'rb') as f:
                elffile = ELFFile(f)

                # Build PLT map
                plt_map = {}
                rel_plt = elffile.get_section_by_name('.rela.plt') or elffile.get_section_by_name('.rel.plt')
                dynsym = elffile.get_section_by_name('.dynsym')

                if rel_plt and dynsym:
                    for relocation in rel_plt.iter_relocations():
                        symbol_index = relocation['r_info_sym']
                        symbol = dynsym.get_symbol(symbol_index)
                        # The relocation address is where the jump is, but we want the PLT entry address
                        # This is very simplified and varies by arch/ABI
                        # For now, let's just keep the symbol names
                        pass

                # Extract architecture
                arch = elffile.get_machine_arch()
                md = None
                if arch == 'x64':
                    md = Cs(CS_ARCH_X86, CS_MODE_64)
                elif arch == 'ARM':
                    md = Cs(CS_ARCH_ARM, CS_MODE_ARM)
                else:
                    md = Cs(CS_ARCH_X86, CS_MODE_64) # Fallback

                # Extract symbols
                symtab = elffile.get_section_by_name('.symtab')
                if symtab:
                    for symbol in symtab.iter_symbols():
                        if symbol['st_info']['type'] == 'STT_FUNC' and symbol['st_size'] > 0:
                            name = symbol.name
                            offset = symbol['st_value']
                            size = symbol['st_size']

                            # Get assembly snippet
                            # We need to find the section containing this offset
                            assembly = ""
                            for section in elffile.iter_sections():
                                if section.header['sh_addr'] <= offset < section.header['sh_addr'] + section.header['sh_size']:
                                    section_offset = offset - section.header['sh_addr']
                                    code = section.data()[section_offset:section_offset + min(size, 100)] # Limit disassembly
                                    for i in md.disasm(code, offset):
                                        assembly += f"0x{i.address:x}: {i.mnemonic} {i.op_str}\n"
                                    break

                            # Heuristic for danger score
                            danger_score = 0
                            vuln_type = "none"

                            # Check for suspicious calls or instructions
                            suspicious_calls = ['gets', 'strcpy', 'strcat', 'scanf', 'system', 'exec', 'popen']

                            # Look for calls to PLT or direct names
                            found_suspicious = False
                            for s_call in suspicious_calls:
                                if s_call in assembly or s_call in name:
                                    found_suspicious = True
                                    if s_call in ['gets', 'strcpy', 'strcat', 'scanf']:
                                        vuln_type = "buffer_overflow"
                                        danger_score = max(danger_score, 80)
                                    else:
                                        vuln_type = "command_injection"
                                        danger_score = max(danger_score, 90)

                            # Enhanced heuristic: look for stack adjustments without canary
                            if "sub rsp" in assembly and "mov rax, qword ptr [rbp - 8]" not in assembly and vuln_type == "buffer_overflow":
                                danger_score += 10

                            # Generate a hash for the function code
                            func_hash = hashlib.sha256(code).hexdigest()

                            # Extract calls from disassembly
                            calls = []
                            for i in md.disasm(code, offset):
                                if i.mnemonic == 'call':
                                    target = i.op_str
                                    # Try to resolve hex target
                                    is_indirect = target.startswith('[')
                                    calls.append({
                                        "callee_name": target,
                                        "offset": hex(i.address),
                                        "is_indirect": is_indirect
                                    })

                            func = models.Function(
                                binary_id=binary.id,
                                name=name,
                                offset=hex(offset),
                                size=size,
                                hash=func_hash,
                                assembly_snippet=assembly if assembly else "Disassembly not available",
                                python_like=f"# Decompiled (pseudo)\ndef {name}():\n    # ... logic ...\n    pass",
                                danger_score=danger_score,
                                vuln_type=vuln_type
                            )
                            db.add(func)
                            db.flush() # Get the function ID

                            # Save calls
                            for c_data in calls:
                                call_obj = models.FunctionCall(
                                    caller_id=func.id,
                                    callee_name=c_data["callee_name"],
                                    offset=c_data["offset"],
                                    is_indirect=c_data["is_indirect"]
                                )
                                db.add(call_obj)

                # Resolve calls within the binary
                binary_funcs = db.query(models.Function).filter(models.Function.binary_id == binary.id).all()
                name_map = {f.name: f.id for f in binary_funcs}
                offset_map = {f.offset: f.id for f in binary_funcs}

                binary_calls = db.query(models.FunctionCall).join(models.Function, models.FunctionCall.caller_id == models.Function.id).filter(models.Function.binary_id == binary.id).all()
                for call in binary_calls:
                    if call.callee_name in name_map:
                        call.callee_id = name_map[call.callee_name]
                    elif call.callee_name.startswith('0x'):
                        # Normalize hex for matching
                        try:
                            norm_hex = hex(int(call.callee_name, 16))
                            if norm_hex in offset_map:
                                call.callee_id = offset_map[norm_hex]
                        except: pass

                # Also check dynamic symbols for imports
                dynsym = elffile.get_section_by_name('.dynsym')
                if dynsym:
                    for symbol in dynsym.iter_symbols():
                        if symbol['st_info']['type'] == 'STT_FUNC' and symbol['st_value'] == 0:
                            # This is an import
                            if any(s in symbol.name for s in ['gets', 'strcpy', 'system']):
                                # Add as a "external" function or log it
                                pass

                db.commit()
                return True
        except Exception as e:
            print(f"Error analyzing ELF: {e}")
            return False

    @staticmethod
    def simulate_binary_ingestion(db: Session, device_id: int, path: str):
        """
        Simulates uploading a binary and discovering functions.
        """
        binary = models.Binary(
            device_id=device_id,
            path=path,
            hash="simulated_hash_12345",
            arch="x86_64",
            file_type="ELF",
            size=102400
        )
        db.add(binary)
        db.flush()

        # Create some simulated functions
        functions_data = [
            {
                "name": "main",
                "offset": "0x401000",
                "size": 256,
                "assembly_snippet": "0x401000: push rbp\n0x401001: mov rbp, rsp\n0x401004: sub rsp, 0x90\n0x401008: lea rdi, [rbp-0x80]\n0x40100c: call gets\n0x401011: leave\n0x401012: ret",
                "python_like": "def main():\n    buffer = bytearray(128)\n    user_input = get_input()\n    strcpy(buffer, user_input)  # DANGER\n    return 0",
                "danger_score": 80,
                "vuln_type": "buffer_overflow"
            },
            {
                "name": "process_input",
                "offset": "0x401200",
                "size": 512,
                "assembly_snippet": "0x401200: push rbp\n0x401201: mov rbp, rsp\n0x401204: lea rdi, [rbp-0x20]\n0x401208: call scanf\n0x40120d: leave\n0x40120e: ret",
                "python_like": "def process_input():\n    buf = bytearray(32)\n    scanf('%s', buf)\n    return",
                "danger_score": 60,
                "vuln_type": "buffer_overflow"
            }
        ]

        for func_data in functions_data:
            # Add a simulated hash for simulated functions
            sim_hash = hashlib.sha256(func_data['assembly_snippet'].encode()).hexdigest()
            function = models.Function(binary_id=binary.id, hash=sim_hash, **func_data)
            db.add(function)

        db.commit()
        return binary
