import asyncio
import json
from datetime import datetime, timedelta

import aiohttp
import pandas as pd

from utils.tools import color, logging, make_filepath

async def fetch(ss: object, url: str, params: dict):
    while True:
        async with ss.get(url, params=params) as rsp:
            if rsp.status == 429:
                logging.error("Attention Rate Limit API")
                await asyncio.sleep(10)
                continue
            return await rsp.json()


async def get_all_movies(ss, config: dict, start_date: str, end_date: str):
    params = {
        "api_key": config["tmdb_api_key"],
        "include_adult": "False",
        "language": config["language"],
        "sort_by": "primary_release_date.desc",
        "primary_release_date.gte": start_date,
        "primary_release_date.lte": end_date,
        "vote_average.gte": str(config["tmdb_rating_avg"]),
        "vote_count.gte": str(config["tmdb_votes_min"]),
        "with_runtime.gte": str(config["tmdb_duration_min"]),
        "with_runtime.lte": str(config["tmdb_duration_max"]),
        "without_genres": "Documentary",
        "page": 1,
    }
    rsp = await fetch(ss, config["url_discover"], params=params)
    total_pages = min(rsp["total_pages"], 500)
    tasks = [
        asyncio.ensure_future(
            fetch(ss, config["url_discover"], {**params, "page": page})
        )
        for page in range(1, total_pages + 1)
    ]
    rsps = await asyncio.gather(*tasks)
    return [r["results"] for r in rsps if r and "results" in r]


async def fetch_movies_ids(ss: object, config: dict):
    start_date = datetime(config["tmdb_date"], 1, 1)
    end_date = datetime.now()
    step = timedelta(days=30)
    list_id_tmdb = set()
    while start_date < end_date:
        segment_end = min(start_date + step, end_date)
        movies = await get_all_movies(
            ss,
            config,
            start_date.strftime("%Y-%m-%d"),
            segment_end.strftime("%Y-%m-%d"),
        )
        list_id_tmdb.update(m["id"] for mb in movies for m in mb)
        start_date = segment_end + timedelta(days=1)
    return list(list_id_tmdb)


async def get_movie_details(ss: object, config: dict, TMdb_id: int):
    params = {
        "api_key": config["tmdb_api_key"],
        "include_adult": "False",
        "language": config["language"],
        "append_to_response": "keywords,credits,videos",
    }
    base_url = f"{config['url_movie']}{TMdb_id}"
    return await fetch(ss, base_url, params=params)


async def main(config: dict):
    async with aiohttp.ClientSession() as ss:
        logging.info("Fetching TMdb ids...")
        tmdb_id_list = await fetch_movies_ids(ss, config)
        logging.info("Creating TMdb Dataframe...")
        taches = []
        for id in tmdb_id_list:
            tache = asyncio.create_task(get_movie_details(ss, config, id))
            taches.append(tache)
            await asyncio.sleep(0.01)
        datas = await asyncio.gather(*taches)
        cc = [
            ("genres", "genres", "name"),
            ("spoken_languages", "spoken_languages", "iso_639_1"),
            ("production_companies_name", "production_companies", "name"),
            ("production_countries", "production_countries", "iso_3166_1"),
        ]
        keys_ = ["imdb_id", "poster_path", "videos"]
        try:
            full = []
            for data in datas:
                if any(key not in data or not data[key] for key in keys_):
                    logging.error(color(data, "red"))
                    continue

                for k, c, v in cc:
                    data[k] = [k[v] for k in data[c]]

                data["keywords"] = [
                    n["name"]
                    for n in data["keywords"]["keywords"][
                        : config["tmdb_keywords_max"]
                    ]
                ]
                condi_acteur = [
                    n
                    for n in data["credits"]["cast"]
                    if n["known_for_department"] == "Acting"
                    and n["order"] <= config["tmdb_actors_max"] - 1
                ]
                condi_director = [
                    n for n in data["credits"]["crew"] if n["job"] == "Director"
                ]
                data["actors"] = [n["name"] for n in condi_acteur]
                data["actors_ids"] = [n["id"] for n in condi_acteur]
                data["director"] = [n["name"] for n in condi_director]
                data["director_ids"] = [n["id"] for n in condi_director]
                data["url"] = f"https://www.imdb.com/title/{data['imdb_id']}"
                data[
                    "image"
                ] = f"https://image.tmdb.org/t/p/w500{data['poster_path']}"
                if data["videos"]["results"]:
                    data["youtube"] = [
                        f"https://www.youtube.com/watch?v={n['key']}"
                        for n in data["videos"]["results"]
                    ][0]
                else:
                    data[
                        "youtube"
                    ] = f"https://www.youtube.com/watch?v=dQw4w9WgXcQ"

                to_pop = [
                    "videos",
                    "video",
                    "credits",
                    "homepage",
                    "belongs_to_collection",
                    "adult",
                    "original_language",
                    "backdrop_path",
                    "spoken_languages",
                    "status",
                    "original_title",
                    "production_companies",
                    "poster_path",
                ]
                for tp in to_pop:
                    data.pop(tp)
                full.append(data)
        except KeyError as e:
            print(e)

    df = pd.DataFrame(full)

    df["actors_ids"] = df["actors_ids"].apply(json.dumps)
    df["director_ids"] = df["director_ids"].apply(json.dumps)
    df["release_date"] = pd.to_datetime(df["release_date"])
    logging.info("Cleaning...")
    df.reset_index(drop="index", inplace=True)
    logging.info("Saving updated TMdb dataframe...")
    base_ = make_filepath(config["path_streamlit"])
    base_ = base_.lstrip("../")
    df.to_parquet(f"{base_}/machine_learning.parquet")
    return df