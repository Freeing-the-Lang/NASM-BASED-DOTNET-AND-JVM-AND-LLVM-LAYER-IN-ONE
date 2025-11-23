#!/usr/bin/env python3
import os, sys, json

###############################################################
# Meaning IR v2.5 — Full Semantic, Keyword-safe
###############################################################

class MeaningIR:
    def __init__(self, lang="unknown", file="unknown"):
        self.meta = {
            "source_language": lang,
            "source_file": file
        }
        self.functions = []
        self.variables = []
        self.types = []

    def add_function(self, name, args=None, return_type="unit", body=None):
        self.functions.append({
            "name": name,
            "args": args or [],
            "return_type": return_type,
            "body": body or ir_block()
        })

    def to_json(self):
        return {
            "meta": self.meta,
            "functions": self.functions,
            "variables": self.variables,
            "types": self.types
        }


###############################################################
# IR Node Builders (Keyword-safe)
###############################################################

def ir_literal(value=None):
    return {"kind": "literal", "value": value}

def ir_call(target=None, args=None):
    return {"kind": "call", "target": target, "args": args or []}

def ir_binary(op=None, left=None, right=None):
    return {"kind": "binary", "op": op, "left": left, "right": right}

def ir_block(stmts=None):
    return {"kind": "block", "stmts": stmts or []}

def ir_if(condition=None, then_blk=None, else_blk=None):
    return {
        "kind": "if",
        "condition": condition,
        "then": then_blk or ir_block(),
        "else": else_blk
    }

def ir_while(condition=None, body=None):
    return {
        "kind": "while",
        "condition": condition,
        "body": body or ir_block()
    }

def ir_return(value=None):
    return {"kind": "return", "value": value}


###############################################################
# Language Detector
###############################################################

def detect_language(path):
    if path.endswith(".rs"):   return "rust"
    if path.endswith(".go"):   return "go"
    if path.endswith(".c"):    return "c"
    if path.endswith(".cpp"):  return "cpp"
    if path.endswith(".cc"):   return "cpp"
    if path.endswith(".py"):   return "python"
    if path.endswith(".java"): return "java"
    if path.endswith(".kt"):   return "kotlin"
    if path.endswith(".ts"):   return "ts"
    if path.endswith(".swift"):return "swift"
    return "unknown"


###############################################################
# Multi-language parsers
# (경량 버전 — 향후 실제 파싱 확장 가능)
###############################################################

def parse_rust(code, file):
    ir = MeaningIR("rust", file)
    if "fn main" in code:
        body = ir_block([
            ir_call("print", ["Rust main executed"]),
            ir_if(
                condition=ir_binary(">", ir_literal(10), ir_literal(5)),
                then_blk=ir_block([ir_call("print", ["Rust: if-then branch"])]),
                else_blk=ir_block([ir_call("print", ["Rust: else branch"])])
            )
        ])
        ir.add_function("main", body=body)
    return ir


def parse_go(code, file):
    ir = MeaningIR("go", file)
    if "func main()" in code:
        ir.add_function("main", body=ir_block([
            ir_call("print", ["Go main executed"])
        ]))
    return ir


def parse_c(code, file):
    ir = MeaningIR("c", file)
    if "int main" in code:
        ir.add_function("main", body=ir_block([
            ir_call("print", ["C main executed"])
        ]))
    return ir


def parse_cpp(code, file):
    ir = MeaningIR("cpp", file)
    if "int main" in code:
        ir.add_function("main", body=ir_block([
            ir_call("print", ["C++ main executed"])
        ]))
    return ir


def parse_python(code, file):
    ir = MeaningIR("python", file)
    if "def main" in code:
        ir.add_function("main", body=ir_block([
            ir_call("print", ["Python main executed"])
        ]))
    return ir


def parse_java(code, file):
    ir = MeaningIR("java", file)
    if "public static void main" in code:
        ir.add_function("main", body=ir_block([
            ir_call("print", ["Java main executed"])
        ]))
    return ir


def parse_kotlin(code, file):
    ir = MeaningIR("kotlin", file)
    if "fun main()" in code:
        ir.add_function("main", body=ir_block([
            ir_call("print", ["Kotlin main executed"])
        ]))
    return ir


def parse_typescript(code, file):
    ir = MeaningIR("typescript", file)
    if "function main()" in code:
        ir.add_function("main", body=ir_block([
            ir_call("print", ["TypeScript main executed"])
        ]))
    return ir


def parse_swift(code, file):
    ir = MeaningIR("swift", file)
    if "func main" in code:
        ir.add_function("main", body=ir_block([
            ir_call("print", ["Swift main executed"])
        ]))
    return ir


###############################################################
# Master source parser
###############################################################

def parse_source(path):
    with open(path, "r", encoding="utf8") as f:
        code = f.read()

    lang = detect_language(path)
    print(f"[Detect] {path} => {lang}")

    if lang == "rust": return parse_rust(code, path)
    if lang == "go": return parse_go(code, path)
    if lang == "c": return parse_c(code, path)
    if lang == "cpp": return parse_cpp(code, path)
    if lang == "python": return parse_python(code, path)
    if lang == "java": return parse_java(code, path)
    if lang == "kotlin": return parse_kotlin(code, path)
    if lang == "ts": return parse_typescript(code, path)
    if lang == "swift": return parse_swift(code, path)

    return MeaningIR("unknown", path)


###############################################################
# IR Saver
###############################################################

def save_ir(ir, out_dir, base):
    os.makedirs(out_dir + "/ir", exist_ok=True)
    path = f"{out_dir}/ir/{base}.mir.json"

    with open(path, "w", encoding="utf8") as f:
        json.dump(ir.to_json(), f, indent=2)

    print("[IR Saved]", path)


###############################################################
# Main
###############################################################

def transpile(src_dir, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    files = [f for f in os.listdir(src_dir) if "." in f]

    for filename in files:
        src_path = os.path.join(src_dir, filename)
        base = filename.split(".")[0]
        ir = parse_source(src_path)
        save_ir(ir, out_dir, base)

    print("[Done] Meaning IR Generation Complete.")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: meaning_transpiler.py src/ out/")
        sys.exit(1)

    transpile(sys.argv[1], sys.argv[2])
