"""G43-R70 bounded, side-effect-free exact arithmetic answers. Not a general math solver."""
from __future__ import annotations
import ast
import re
from decimal import Decimal, localcontext, ROUND_HALF_UP

N=r"(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d+)?"
def d(x): return Decimal(str(x).replace(',',''))
def fmt(v):
    return format(v,'f').rstrip('0').rstrip('.') if '.' in format(v,'f') else format(v,'f')

def compute_expr(text):
    if len(text)>180 or not re.fullmatch(r'[\d\s,().+\-*/]+',text): return None
    expr=text.replace(',','')
    tree=ast.parse(expr,mode='eval')
    def walk(node,depth=0):
        if depth>12: raise ValueError('deep')
        if isinstance(node,ast.Expression): return walk(node.body,depth+1)
        if isinstance(node,ast.Constant) and type(node.value) in (int,float):
            return Decimal(str(node.value))
        if isinstance(node,ast.UnaryOp) and isinstance(node.op,(ast.UAdd,ast.USub)):
            x=walk(node.operand,depth+1)
            return x if isinstance(node.op,ast.UAdd) else -x
        if isinstance(node,ast.BinOp) and isinstance(node.op,(ast.Add,ast.Sub,ast.Mult,ast.Div)):
            a,b=walk(node.left,depth+1),walk(node.right,depth+1)
            if isinstance(node.op,ast.Add):return a+b
            if isinstance(node.op,ast.Sub):return a-b
            if isinstance(node.op,ast.Mult):return a*b
            if b==0:raise ValueError('divide by zero')
            return a/b
        raise ValueError('unsafe expression')
    with localcontext() as ctx:
        ctx.prec=40
        return walk(tree)

def answer(question):
    if not isinstance(question,str) or len(question)>650:return None
    q=' '.join(question.strip().split())
    with localcontext() as ctx:
        ctx.prec=40
        # Complete mathematical expression, never a two-operand prefix.
        m=re.match(r"^(?:calculate|compute|evaluate|what(?:'s| is))\s+",q,re.I)
        if m:
            expr=q[m.end():]
            expr=re.split(r"\.\s+(?:Give|Show|Explain|Verify)\b",expr,maxsplit=1,flags=re.I)[0]
            expr=re.sub(r"\s+exactly\.?$","",expr,flags=re.I).strip().rstrip('.?!').strip()
            # Require a complete arithmetic expression; punctuation and explanations
            # after the expression do not get interpreted as operators.
            if re.search(r'\d\s*[+*/\-]\s*\d|\)\s*[/+*\-]',expr):
                try:
                    value=compute_expr(expr)
                    if value is not None:return f"**{fmt(value)}**. Verified from the complete expression: {expr} = {fmt(value)}."
                except (ValueError,ArithmeticError,SyntaxError):pass
        m=re.fullmatch(rf'A quantity rises from ({N}) to ({N})\. What is its percentage change to 2 decimal places\?',q,re.I)
        if m and d(m[1])!=0:
            pct=(d(m[2])-d(m[1]))/d(m[1])*100
            return f"**{pct.quantize(Decimal('0.01'),rounding=ROUND_HALF_UP):.2f}%**. Change = ({m[2]} − {m[1]}) ÷ {m[1]} × 100."
        m=re.fullmatch(rf'You pay \$({N}) for equipment and then \$({N}) in repairs\. If its resale value is \$({N}), what is net profit in dollars\?',q,re.I)
        if m:
            profit=d(m[3])-d(m[1])-d(m[2])
            return f"**Net {'profit' if profit>=0 else 'loss'}: ${abs(profit):,.2f}**. ${d(m[3]):,.2f} − ${d(m[1]):,.2f} − ${d(m[2]):,.2f} = ${profit:,.2f}."
        m=re.fullmatch(rf'A project has ({N}) units divided into ({N}) equal batches\. What is the quotient and remainder\?',q,re.I)
        if m:
            a,b=d(m[1]),d(m[2])
            if a>=0 and b>0 and a==int(a) and b==int(b):
                quotient,remainder=divmod(int(a),int(b))
                return f"**Quotient: {quotient}; remainder: {remainder}.** Check: {quotient} × {int(b)} + {remainder} = {int(a)}."
    return None
