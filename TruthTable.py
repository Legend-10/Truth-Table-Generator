import streamlit as st
from sympy import SympifyError, S, symbols, parse_expr
from sympy.logic.boolalg import Boolean
import itertools
import pandas as pd

def generate_truth_table(expression):
    try:
        expr = parse_expr(expression, evaluate=False)
        if not isinstance(expr, Boolean):
            raise SympifyError("Not a valid boolean expression")
        variables = sorted(expr.free_symbols, key=str)
        truth_combinations = itertools.product([False, True], repeat=len(variables))
        table = []
        for combo in truth_combinations:
            assignments = {var: S.true if val else S.false for var, val in zip(variables, combo)}
            result = expr.subs(assignments).simplify()
            table.append([*combo, result == S.true])
        df = pd.DataFrame(table, columns=[str(var) for var in variables] + ['Result'])
        return df
    
    except SympifyError as e:
        st.error(f"Invalid expression: {e}")
        return None

st.title("Logical Expression Truth Table Generator")

help_text = """
Enter a logical expression using:
- Variables (e.g., A, B, C)
- Operators: 
  - AND: & or ∧ 
  - OR: | or ∨ 
  - NOT: ~ or ¬ 
  - IMPLIES: >> or → 
  
Examples: 
- A & (B | C)
- (P → Q) ∧ ¬Q
"""

expression = st.text_input("Enter logical expression:", help=help_text)

if expression:
    processed_expr = (
        expression.replace('∧', '&')
        .replace('∨', '|')
        .replace('¬', '~')
        .replace('→', '>>')
    )
    
    truth_table = generate_truth_table(processed_expr)
    
    if truth_table is not None:
        st.subheader("Truth Table")
        st.dataframe(truth_table.style.format(lambda x: "True" if x else "False"))
        st.subheader("Parsed Expression")
        try:
            from sympy import latex
            st.latex(f"{latex(parse_expr(processed_expr))}")
        except:
            st.code(processed_expr)