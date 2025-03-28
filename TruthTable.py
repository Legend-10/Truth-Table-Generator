import streamlit as st
from sympy import SympifyError, S, symbols, parse_expr, to_cnf, to_dnf, to_nnf, latex
from sympy.logic.boolalg import Boolean, Equivalent, Implies, And, Or, Not, Xor
import itertools
import pandas as pd
import matplotlib.pyplot as plt
import graphviz

# Configuration
st.set_page_config(page_title="Logic Toolbox", layout="wide")

def evaluate_expression_steps(expr, assignments):
    """Custom implementation of step-by-step evaluation"""
    steps = []
    try:
        parsed = parse_expr(expr, evaluate=False)
        for sub_expr in parsed.args:
            step = {
                "operation": type(sub_expr).__name__,
                "result": sub_expr.subs(assignments).simplify()
            }
            steps.append(step)
        steps.append({
            "operation": "Final Result",
            "result": parsed.subs(assignments).simplify()
        })
    except:
        pass
    return steps

def create_parse_tree(expr):
    """Create simple parse tree using Graphviz"""
    dot = graphviz.Digraph()
    _build_tree(dot, parse_expr(str(expr)))
    return dot

def _build_tree(dot, node, parent=None, node_id=0):
    current_id = str(node_id)
    dot.node(current_id, str(node.__class__.__name__))
    if parent:
        dot.edge(parent, current_id)
    for i, child in enumerate(node.args):
        _build_tree(dot, child, current_id, node_id*10 + i + 1)

def generate_truth_table(expression):
    try:
        expr = parse_expr(expression, evaluate=False)
        if not isinstance(expr, Boolean):
            raise SympifyError("Not a valid boolean expression")
        
        # Get and sort the variables
        variables = sorted(expr.free_symbols, key=str)
        truth_combinations = itertools.product([False, True], repeat=len(variables))
        
        table = []
        for combo in truth_combinations:
            assignments = {var: val for var, val in zip(variables, combo)}
            result = expr.subs(assignments).simplify()
            # Convert the boolean result to a string "True" or "False"
            table.append([*combo, "True" if result == S.true else "False"])
        
        df = pd.DataFrame(table, columns=[str(var) for var in variables] + ['Result'])
        return df, variables, []
    
    except SympifyError as e:
        st.error(f"Expression Error: {str(e)}")
        return None, None, None

def main():
    st.title("🖩 Advanced Logic Expression Analyzer")
    
    with st.sidebar:
        st.header("Settings")
        visualization_type = st.selectbox(
            "Visualization Mode",
            ["Truth Table", "Parse Tree"]
        )
        show_steps = st.checkbox("Show Evaluation Steps", True)
        normalize_form = st.selectbox(
            "Normal Form Conversion",
            ["None", "CNF", "DNF", "NNF"]
        )
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("Expression Input")
        expr = st.text_input("Enter logical expression:", 
                           help="Use variables & operators: ~, &, |, >>, ^ for XOR")
        
        if expr:
            expr_clean = (expr.replace('∧', '&').replace('∨', '|')
                          .replace('¬', '~').replace('→', '>>').replace('⊕', '^'))
            
            try:
                parsed_expr = parse_expr(expr_clean, evaluate=False)
                
                if normalize_form == "CNF":
                    parsed_expr = to_cnf(parsed_expr)
                elif normalize_form == "DNF":
                    parsed_expr = to_dnf(parsed_expr)
                elif normalize_form == "NNF":
                    parsed_expr = to_nnf(parsed_expr)
                
                st.markdown(f"**Normalized Form ({normalize_form}):**")
                st.latex(f"{latex(parsed_expr)}")
                
                st.markdown("**Properties:**")
                col1a, col1b, col1c = st.columns(3)
                with col1a:
                    st.metric("Variables", len(parsed_expr.free_symbols))
                with col1b:
                    st.metric("Operators", count_operators(parsed_expr))
                with col1c:
                    complexity = "Simple" if len(parsed_expr.free_symbols) < 4 else "Complex"
                    st.metric("Complexity", complexity)
                
            except SympifyError as e:
                st.error(f"Parsing Error: {str(e)}")
    
    with col2:
        if expr:
            st.subheader("Analysis Results")
            tab1, tab2 = st.tabs(["Truth Table", "Visualization"])
            
            with tab1:
                df, variables, steps = generate_truth_table(str(parsed_expr))
                if df is not None:
                    # We now display the truth table with True/False text
                    st.dataframe(df, use_container_width=True)
            
            with tab2:
                if visualization_type == "Parse Tree":
                    st.graphviz_chart(create_parse_tree(str(parsed_expr)))

def count_operators(expr):
    count = 0
    if isinstance(expr, (And, Or, Implies, Xor)):
        count += 1
        for arg in expr.args:
            count += count_operators(arg)
    elif isinstance(expr, Not):
        count += 1
        count += count_operators(expr.args[0])
    return count

if __name__ == "__main__":
    main()
