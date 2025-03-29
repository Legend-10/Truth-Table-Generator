import streamlit as st
from sympy import SympifyError, S, parse_expr
from sympy.logic.boolalg import Boolean
import itertools
import pandas as pd

st.markdown("""
<style>
.help-icon {
    position: fixed;
    top: 10px;
    right: 10px;
    cursor: pointer;
    z-index: 1000;
    font-size: 20px;
    color: #ffffff;
    background-color: #4F8BF9;
    border-radius: 50%;
    width: 30px;
    height: 30px;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.help-icon:hover {
    background-color: #3B6DB0;
}

.expander-content {
    margin-top: 40px;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="help-icon">ℹ️</div>', unsafe_allow_html=True)
with st.expander("", expanded=False):
    st.markdown("""
    **Logical Expression Help**
    
    **Supported Operators:**
    - AND: `&` or `∧`
    - OR: `|` or `∨` 
    - NOT: `~` or `¬`
    - IMPLIES: `>>` or `→`
    
    **Examples:**
    ```python
    A & (B | C)
    (P → Q) ∧ ¬Q
    ~(A | B) → C
    ```
    
    **Built with:**
    - Streamlit 🎈
    - SymPy 🔢
    - Pandas 🗂️
    """)

st.title("Logical Expression Truth Table Generator")

def generate_truth_table(expression):
    try:
        expr = parse_expr(expression, evaluate=False)
        if not isinstance(expr, Boolean):
            raise SympifyError("Not a valid boolean expression")
        variables = sorted(expr.free_symbols, key=str)
        truth_combinations = itertools.product([False, True], repeat=len(variables))
        table = []
        for combo in truth_combinations:
            combo_str = ["True" if val else "False" for val in combo]
            assignments = {var: S.true if val else S.false for var, val in zip(variables, combo)}
            result = expr.subs(assignments).simplify()
            result_str = "True" if result == S.true else "False"
            table.append(combo_str + [result_str])
        df = pd.DataFrame(table, columns=[str(var) for var in variables] + ['Result'])
        return df
    except SympifyError as e:
        st.error(f"Invalid expression: {e}")
        return None

expression = st.text_input("Enter logical expression:", placeholder="Example: (A & B) | ~C")

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
        st.dataframe(truth_table.style.highlight_max(axis=0, color='#d8f3dc'), use_container_width=True)
        
        st.subheader("Expression Analysis")
        try:
            from sympy import latex
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**Parsed structure:**")
                st.latex(f"{latex(parse_expr(processed_expr))}")
            with col2:
                st.markdown("**Symbol count:**")
                variables = sorted(parse_expr(processed_expr).free_symbols, key=str)
                st.code(f"Variables: {len(variables)}\nOperators: {processed_expr.count('&') + processed_expr.count('|') + processed_expr.count('~') + processed_expr.count('>>')}")
        except Exception as e:
            st.error(f"Error analyzing expression: {e}")
