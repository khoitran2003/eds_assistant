import re
from typing import List
import unicodedata
from typing import Dict
from datetime import time

from openai import OpenAI

from . import get_env_var


def get_openai_embedding(text: str) -> List[float]:
    try:
        openai_api_key = get_env_var("OPENAI_API_KEY")
        if not openai_api_key:
            raise ValueError("OPENAI_API_KEY is not set")

        client = OpenAI(api_key=openai_api_key)
        response = client.embeddings.create(input=text, model="text-embedding-3-small")
        return response.data[0].embedding
    except Exception as e:
        print(f"Error generating embedding: {e}")
        return []


def clean_input_query(query: str) -> str:
    cleaned = unicodedata.normalize("NFKC", query)
    cleaned = cleaned.replace("user", "")
    cleaned = re.sub(r"\s+", " ", cleaned)
    cleaned = (
        cleaned.replace("“", "").replace("”", "").replace("‘", "").replace("’", "")
    )
    cleaned = re.sub(r"[\x00-\x1F\x7F]", "", cleaned)
    cleaned = re.sub(
        r"(\d+)\s*(am|pm)\b",
        lambda m: f"{m.group(1)} {m.group(2).upper()}",
        cleaned,
        flags=re.IGNORECASE,
    )
    return cleaned.strip()


# def read_csv_file(file_path: str) -> pd.DataFrame:
#     try:
#         data = pd.read_csv(file_path)
#         return data
#     except Exception as e:
#         print(f"Error reading CSV file: {e}")
#         return pd.DataFrame()

# def read_json_file(file_path: str) -> Dict:
#     try:
#         data = json.load(open(file_path))
#         return data
#     except Exception as e:
#         print(f"Error reading JSON file: {e}")
#         return {}


def parse_schedule(schedule_str: str) -> Dict[str, tuple]:
    day_slots = {}
    for part in schedule_str.split(";"):
        part = part.strip()
        if not part:
            continue
        m = re.match(
            r"^(Mon|Tue|Wed|Thu|Fri|Sat|Sun)\s+(\d{2}:\d{2})-(\d{2}:\d{2})$", part
        )
        if not m:
            raise ValueError(f"Invalid segment: {part!r}")
        day, start_s, end_s = m.groups()
        day_slots[day] = (
            time(*map(int, start_s.split(":")), tzinfo=None),
            time(*map(int, end_s.split(":")), tzinfo=None),
        )
    return day_slots


def is_time_in_schedule(schedule_str: str, time_str: str) -> bool:
    schedule = parse_schedule(schedule_str)
    day, t = time_str.split(" ")
    try:
        day_slot = schedule.get(day)
        if not day_slot:
            return False
        start_time, end_time = day_slot
        t = time(*map(int, t.split(":")), tzinfo=None)
        return start_time <= t <= end_time

    except Exception as e:
        print(f"Error parsing schedule: {e}")
        return False
