from datetime import datetime
import os
import json


def store_data_as_json(data, path, source) -> None:
    data_dir = path

    if not os.path.exists(data_dir):
        os.makedirs(data_dir)

    output_file = os.path.join(
        data_dir,
        f"{source}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
    )

    print(f"Saving {len(data)} entries to {output_file}...")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    print(f"✅ Saved {len(data)} entries to {output_file}")
