def highlight_results(results):
    highlighted = []

    for r in results:
        if r["risk"] == "HIGH":
            color = "🔴"
        elif r["risk"] == "MEDIUM":
            color = "🟡"
        else:
            color = "🟢"

        line = f"{color} [{r['risk']} | {r['confidence']}] {r['clause']}"
        explanation = f"   → {r['explanation']}"

        highlighted.append(line)
        highlighted.append(explanation)

    return "\n".join(highlighted)