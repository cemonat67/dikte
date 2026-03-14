import json
import random
from datetime import datetime, timezone
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
CONFIG_PATH = BASE_DIR.parent / "config" / "feeder_config.json"


class SapEventGenerator:
    def __init__(self, config: dict):
        self.config = config
        self.facility = config["facility"]
        self.process_lines = config["process_lines"]
        self.assets = config["assets"]
        self.ranges = config["ranges"]
        self.order_prefix = config["order"]["prefix"]
        self.batch_min_events = config["batch"]["min_events"]
        self.batch_max_events = config["batch"]["max_events"]

        self.order_counter = 1
        self.batch_counter = 1
        self.current_batch_event_count = 0
        self.current_batch_target_events = 0
        self.current_order_id = None
        self.current_batch_id = None
        self.current_process_line = None
        self.current_asset_id = None

        random.seed(42)

    def _next_order_id(self) -> str:
        today = datetime.now().strftime("%Y%m%d")
        order_id = f"{self.order_prefix}-{today}-{self.order_counter:04d}"
        self.order_counter += 1
        return order_id

    def _next_batch_id(self) -> str:
        today = datetime.now().strftime("%Y%m%d")
        batch_id = f"BAT-{today}-{self.batch_counter:04d}"
        self.batch_counter += 1
        return batch_id

    def _pick_float(self, key: str, digits: int = 2) -> float:
        low, high = self.ranges[key]
        return round(random.uniform(low, high), digits)

    def _pick_int(self, key: str) -> int:
        low, high = self.ranges[key]
        return random.randint(int(low), int(high))

    def _start_new_batch(self):
        self.current_order_id = self._next_order_id()
        self.current_batch_id = self._next_batch_id()
        self.current_process_line = random.choice(self.process_lines)
        self.current_asset_id = random.choice(self.assets)
        self.current_batch_event_count = 0
        self.current_batch_target_events = random.randint(
            self.batch_min_events,
            self.batch_max_events
        )

    def generate_event(self) -> dict:
        if (
            self.current_batch_id is None
            or self.current_batch_event_count >= self.current_batch_target_events
        ):
            self._start_new_batch()

        self.current_batch_event_count += 1

        production_kg = self._pick_int("production_kg")
        energy_kwh = self._pick_float("energy_kwh")
        water_m3 = self._pick_float("water_m3")
        natural_gas_m3 = self._pick_float("natural_gas_m3")
        wastewater_m3 = self._pick_float("wastewater_m3")
        cod_mg_l = self._pick_float("cod_mg_l")
        bod_mg_l = self._pick_float("bod_mg_l")
        tss_mg_l = self._pick_float("tss_mg_l")
        ph = self._pick_float("ph")
        co2_kg = self._pick_float("co2_kg")

        event = {
            "facility": self.facility,
            "order_id": self.current_order_id,
            "batch_id": self.current_batch_id,
            "process_line": self.current_process_line,
            "asset_id": self.current_asset_id,
            "event_timestamp": datetime.now(timezone.utc).isoformat(),
            "production_kg": production_kg,
            "energy_kwh": energy_kwh,
            "water_m3": water_m3,
            "natural_gas_m3": natural_gas_m3,
            "wastewater_m3": wastewater_m3,
            "cod_mg_l": cod_mg_l,
            "bod_mg_l": bod_mg_l,
            "tss_mg_l": tss_mg_l,
            "ph": ph,
            "co2_kg": co2_kg
        }

        return event

    def generate_events(self, count: int) -> list[dict]:
        return [self.generate_event() for _ in range(count)]



def load_config() -> dict:
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


if __name__ == "__main__":
    config = load_config()
    generator = SapEventGenerator(config)
    event = generator.generate_event()
    print(json.dumps(event, indent=2))
