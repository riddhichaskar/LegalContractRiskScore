import html

def highlight_results(results):
    highlighted = []

    for r in results:
        if r["risk"] == "HIGH":
            color = "🔴"
        elif r["risk"] == "MEDIUM":
            color = "🟡"
        else:
            color = "🟢"

        safe_clause = html.escape(str(r.get("clause", "")))
        safe_explanation = html.escape(str(r.get("explanation", "")))
        confidence_val = float(r.get("confidence", 0.0)) * 100

        line = f"{color} [{r['risk']} | {confidence_val:.1f}%] {safe_clause}"
        explanation = f"   → Explanation: {safe_explanation}"

        highlighted.append(line)
        highlighted.append(explanation)

    return "\n".join(highlighted)