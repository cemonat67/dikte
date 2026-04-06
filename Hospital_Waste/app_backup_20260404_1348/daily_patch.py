from datetime import timedelta

def fill_gaps(rows, days):
    if not rows:
        return []

    # map by date
    data = {r["reading_date"]: r for r in rows}

    all_dates = sorted(data.keys())
    max_date = max(all_dates)
    min_date = max_date - timedelta(days=days-1)

    result = []
    last_known = None

    current = min_date
    while current <= max_date:
        if current in data:
            row = data[current]
            row["data_quality"] = "actual"
            last_known = row
        else:
            # fallback: forward fill
            if last_known:
                row = dict(last_known)
                row["reading_date"] = current
                row["data_quality"] = "estimated"
            else:
                current += timedelta(days=1)
                continue
        result.append(row)
        current += timedelta(days=1)

    return sorted(result, key=lambda x: x["reading_date"], reverse=True)
