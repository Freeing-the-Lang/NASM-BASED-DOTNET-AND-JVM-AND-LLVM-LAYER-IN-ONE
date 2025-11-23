#!/usr/bin/env python3
import os, json, sys

# ============================================================
# Meaning IR v3 — Typed, Scoped, Callable, Intent-Based IR
# ============================================================

class SemanticNode:
    def to_json(self): raise NotImplementedError

# ----- Values & Symbols -----

class Value(SemanticNode):
    def __init__(self, value): self.value = value
    def to_json(self): return {"intent": "value", "value": self.value}

class TypedValue(SemanticNode):
    def __init__(self, vtype, value): self.vtype = vtype; self.value = value
    def to_json(self): return {"intent": "typed_value", "type": self.vtype, "value": self.value}

class Symbol(SemanticNode):
    def __init__(self, name): self.name = name
    def to_json(self): return {"intent": "symbol", "name": self.name}

# ----- Variables -----

class Declare(SemanticNode):
    def __init__(self, name, vtype, value):
        self.name = name; self.vtype = vtype; self.value = value
    def to_json(self):
        return {
            "intent": "declare",
            "name": self.name,
            "type": self.vtype,
            "value": self.value.to_json()
        }

class Assign(SemanticNode):
    def __init__(self, name, value):
        self.name = name; self.value = value
    def to_json(self):
        return {
            "intent": "assign",
            "target": self.name,
            "value": self.value.to_json()
        }

# ----- Actions -----

class Output(SemanticNode):
    def __init__(self, msg): self.msg = msg
    def to_json(self): return {"intent": "output_text", "payload": self.msg}

class Compare(SemanticNode):
    def __init__(self, op, left, right):
        self.op=op; self.left=left; self.right=right
    def to_json(self):
        return {
            "intent": "compare",
            "operation": self.op,
            "left": self.left.to_json(),
            "right": self.right.to_json()
        }

class Branch(SemanticNode):
    def __init__(self, cond, then_blk, else_blk=None):
        self.cond=cond; self.then_blk=then_blk; self.else_blk=else_blk
    def to_json(self):
        return {
            "intent": "branch",
            "condition": self.cond.to_json(),
            "then": self.then_blk.to_json(),
            "else": self.else_blk.to_json() if self.else_blk else None
        }

class Loop(SemanticNode):
    def __init__(self, cond, body):
        self.cond=cond; self.body=body
    def to_json(self):
        return {
            "intent": "loop_until_break",
            "condition": self.cond.to_json(),
            "body": self.body.to_json()
        }

class Return(SemanticNode):
    def __init__(self, value=None): self.value=value
    def to_json(self):
        return {
            "intent": "return",
            "value": self.value.to_json() if self.value else None
        }

class Call(SemanticNode):
    def __init__(self, name, args):
        self.name=name; self.args=args
    def to_json(self):
        return {
            "intent": "call",
            "target": self.name,
            "args": [a.to_json() for a in self.args]
        }

# ----- Block / Function / Program -----

class Block(SemanticNode):
    def __init__(self, actions): self.actions=actions
    def to_json(self): return {"intent": "block", "actions": [a.to_json() for a in self.actions]}

class Function(SemanticNode):
    def __init__(self, name, args, ret, body):
        self.name=name; self.args=args; self.ret=ret; self.body=body
    def to_json(self):
        return {
            "kind": "function",
            "name": self.name,
            "args": self.args,
            "return_type": self.ret,
            "body": self.body.to_json()
        }

class Program(SemanticNode):
    def __init__(self, functions, meta=None):
        self.functions=functions; self.meta=meta or {}
    def to_json(self):
        return {
            "meta": self.meta,
            "functions": [f.to_json() for f in self.functions]
        }

# ============================================================
# Meaning VM v3
# ============================================================

class VMReturn(Exception):
    def __init__(self, value=None): self.value=value

class Frame:
    def __init__(self): self.env={}

class MeaningVM:
    def __init__(self, ir_json):
        self.functions = {fn["name"]: fn for fn in ir_json["functions"]}
        self.stack=[]

    def push(self): self.stack.append(Frame())
    def pop(self): self.stack.pop()
    @property
    def env(self): return self.stack[-1].env

    def run(self):
        self.push()
        main = self.functions["main"]
        self.exec(main["body"])

    def exec(self, node):
        intent=node.get("intent")

        if intent=="block":
            for a in node["actions"]: self.exec(a); return

        if intent=="declare": self.env[node["name"]] = self.exec(node["value"]); return
        if intent=="assign": self.env[node["target"]] = self.exec(node["value"]); return

        if intent=="symbol": return self.env[node["name"]]
        if intent=="value": return node["value"]
        if intent=="typed_value": return node["value"]

        if intent=="output_text": print(node["payload"]); return

        if intent=="compare":
            l=self.exec(node["left"]); r=self.exec(node["right"])
            if node["operation"]=="greater_than": return l>r
            if node["operation"]=="equal": return l==r
            if node["operation"]=="less_than": return l<r

        if intent=="branch":
            if self.exec(node["condition"]): return self.exec(node["then"])
            else:
                if node["else"]: return self.exec(node["else"])
            return

        if intent=="loop_until_break":
            while self.exec(node["condition"]): self.exec(node["body"])
            return

        if intent=="return":
            val=self.exec(node["value"]) if node["value"] else None
            raise VMReturn(val)

        if intent=="call":
            fn=self.functions[node["target"]]
            args=[self.exec(a) for a in node["args"]]

            self.push()
            for i, arg in enumerate(fn["args"]):
                self.env[arg["name"]] = args[i]

            try:
                self.exec(fn["body"])
            except VMReturn as ret:
                self.pop()
                return ret.value

            self.pop()
            return

        raise Exception(f"Unknown intent: {intent}")

# ============================================================
# Dummy Parser → IR v3 생성
# ============================================================

def parse_to_ir_v3(path):
    main = Function(
        "main", [], "unit",
        Block([
            Declare("x","int",Value(10)),
            Branch(
                Compare("greater_than", Symbol("x"), Value(5)),
                Block([Output("x is greater than 5")])
            ),
            Loop(Value(True), Block([Output("loop"), Return()]))
        ])
    )
    return Program([main], meta={"source":"meaning-ir-v3"})

# ============================================================
# Backend Emitters
# ============================================================

def extract_msg(ir):
    def dfs(n):
        if isinstance(n,dict) and n.get("intent")=="output_text":
            return n["payload"]
        if isinstance(n,dict):
            for v in n.values():
                r=dfs(v); 
                if r: return r
        if isinstance(n,list):
            for x in n:
                r=dfs(x); 
                if r: return r
    return dfs(ir) or "Hello from IR v3"

def emit_backends(ir_obj, out):
    os.makedirs(f"{out}/llvm", exist_ok=True)
    os.makedirs(f"{out}/jvm", exist_ok=True)
    os.makedirs(f"{out}/dotnet", exist_ok=True)
    os.makedirs(f"{out}/native", exist_ok=True)

    ir_json = ir_obj.to_json()
    msg = extract_msg(ir_json)

    open(f"{out}/llvm/main.c","w").write(
        f'#include <stdio.h>\nint main(){{printf("{msg}\\n");}}\n'
    )

    open(f"{out}/jvm/Main.java","w").write(
        f'public class Main{{public static void main(String[]a){{System.out.println("{msg}");}}}}'
    )

    open(f"{out}/dotnet/Program.cs","w").write(
        f'using System;class Program{{static void Main(){{Console.WriteLine("{msg}");}}}}'
    )

    open(f"{out}/native/main.asm","w").write(
f"""global _start
section .text
_start:
    mov rax,1
    mov rdi,1
    mov rsi,msg
    mov rdx,{len(msg)+1}
    syscall
    mov rax,60
    xor rdi,rdi
    syscall
section .data
msg db "{msg}",10
"""
)

# ============================================================
# Main transpile
# ============================================================

def transpile(src, out):
    ir = parse_to_ir_v3(src)
    os.makedirs(out, exist_ok=True)
    open(f"{out}/ir.json","w").write(json.dumps(ir.to_json(),indent=2))
    emit_backends(ir,out)

def run_vm(ir_path):
    ir=json.load(open(ir_path))
    vm=MeaningVM(ir)
    vm.run()

if __name__ == "__main__":
    mode=sys.argv[1]
    if mode=="transpile":
        transpile(sys.argv[2], sys.argv[3])
    elif mode=="runvm":
        run_vm(sys.argv[2])
    else:
        print("usage:")
        print("  meaning_engine.py transpile src/ out/")
        print("  meaning_engine.py runvm out/ir.json")

