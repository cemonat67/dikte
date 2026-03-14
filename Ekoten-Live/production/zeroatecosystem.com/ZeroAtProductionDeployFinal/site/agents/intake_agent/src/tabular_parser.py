from pathlib import Path
import pandas as pd
from .normalize import build_record_from_row

def parse_tabular_file(path: str) -> list[dict]:
    file_path = Path(path)
    suffix = file_path.suffix.lower()

    if suffix == ".csv":
        df = pd.read_csv(file_path, dtype=str, keep_default_na=False)
    elif suffix == ".xlsx":
        df = pd.read_excel(file_path, dtype=str)
        df = df.fillna("")
    else:
        raise ValueError(f"Unsupported tabular file: {suffix}")

    rows = df.to_dict(orient="records")
    records = []

    for idx, row in enumerate(rows, start=1):
        safe_row = {k: ("" if v is None else str(v).strip()) for k, v in row.items()}
        records.append(
            build_record_from_row(
                row=safe_row,
                source_name=file_path.name,
                source_type=suffix.lstrip("."),
                row_index=idx,
            )
        )

    return records
