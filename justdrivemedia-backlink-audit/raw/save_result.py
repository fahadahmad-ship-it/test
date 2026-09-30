"""Extract CSV text from a saved MCP tool-result file into a CSV, print row count + min date."""
import io, json, sys
import pandas as pd
src, out = sys.argv[1], sys.argv[2]
sep = sys.argv[3] if len(sys.argv) > 3 else ","
j = json.load(open(src))
t = j[0]["text"] if isinstance(j, list) else j["data"]
if t.lstrip().startswith("{"):  # Semrush JSON wrapper
    t = json.loads(t)["data"]
df = pd.read_csv(io.StringIO(t), sep=sep)
df.to_csv(out, index=False)
col = next((c for c in ("first_seen_link", "first_seen") if c in df.columns), None)
print(len(df), "rows ->", out, "| min", col, df[col].min() if col else "")
