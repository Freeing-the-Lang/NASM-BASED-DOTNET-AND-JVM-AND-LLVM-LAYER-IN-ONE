#!/usr/bin/env python3
import os, sys, json

###################################################################
# Meaning IR v2.0 (제어 흐름 추가)
###################################################################

class MeaningIR:
    def __init__(self, lang="unknown", file="unknown"):
        self.meta = {
            "source_language": lang,
            "source_file": file
        }
        self.functions = []
        self.variables = []
        self.types = []

    def add_function(self, name, args, return_type, body):
        self.functions.append({
            "name": name,
            "args": args,
            "return_type": return_type,
            "body": body   # body is now a BLOCK IR
        })

###################################################################
# IR Node Builders
###################################################################

def ir_literal(value):
    return {"kind": "literal", "value": value}

def ir_call(name, args):
    return {"kind": "call", "target": name, "args": args}

def ir_binary(op, left, right):
    return {"kind": "binary", "op": op, "left": left, "right": right}

def ir_block(stmts):
    return {"kind": "block", "stmts": stmts}

def ir_if(cond, then_blk, else_blk=None):
    return {
        "kind": "if",
        "condition": cond,
        "then": then_blk,
        "else": else_blk
    }

def ir_while(cond, body):
    return {
        "kind": "while",
        "condition": cond,
        "body": body
    }

def ir_return(val):
    return {"kind": "return", "value": val}

###################################################################
# 언어별 파서 (여전히 경량 — 확장 가능)
###################################################################
# 여기서는 모든 언어에서 "main"의 의미만 추출

def parse_source(path):
    with open(path, "r", encoding="utf8") as f:
        code = f.read()

    # 간단 감지
    if path.endswith(".rs"):   lang = "rust"
    elif path.endswith(".go"): lang = "go"
    elif path.endswith(".c"):  lang = "c"
    elif path.endswith(".py"): lang = "python"
    elif path.endswith(".swift"): lang = "swift"
    elif path.endswith(".java"):  lang = "java"
    elif path.endswith(".kt"):    lang = "kotlin"
    elif path.endswith(".ts"):    lang = "ts"
    elif path.endswith(".cpp"):   lang = "cpp"
    else: lang = "unknown"

    ir = MeaningIR(lang, path)

    # 실제 제어 흐름 예시를 넣어 IR을 생성 (확장 가능)
    # 실제 언어 파싱 확장은 다음 단계에서 추가 가능
    # 여기는 Meaning IR "기능 추가"가 목적
    body = ir_block([
        ir_if(
            condition=ir_binary(">", ir_literal(10), ir_literal(5)),
            then_blk=ir_block([ir_call("print", ["Then branch executed"])]),
            else_blk=ir_block([ir_call("print", ["Else branch executed"])])
        ),
        ir_while(
            cond=ir_literal(True),
            body=ir_block([
                ir_call("print", ["loop"]),
                ir_return(None)
            ])
        )
    ])

    ir.add_function("main", [], "unit", body)
    return ir


###################################################################
# IR 저장
###################################################################

def save_ir(ir, out_dir, base):
    os.makedirs(out_dir + "/ir", exist_ok=True)
    path = f"{out_dir}/ir/{base}.mir.json"
    with open(path, "w", encoding="utf8") as f:
        json.dump({
            "meta": ir.meta,
            "functions": ir.functions,
            "variables": ir.variables,
            "types": ir.types
        }, f, indent=2)
    print("[IR Saved]", path)


###################################################################
# Main
###################################################################

def transpile(src_dir, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    files = [f for f in os.listdir(src_dir) if "." in f]

    for filename in files:
        src_path = os.path.join(src_dir, filename)
        base = filename.split(".")[0]

        ir = parse_source(src_path)
        save_ir(ir, out_dir, base)

    print("[Done] Meaning IR with Control Flow generated.")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: meaning_transpiler.py <src> <out>")
        sys.exit(1)

    transpile(sys.argv[1], sys.argv[2])
