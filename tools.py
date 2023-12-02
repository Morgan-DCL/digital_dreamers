import ast
import json
import logging
import os
import re
from unicodedata import combining, normalize

import hjson
import numpy as np
import pandas as pd
import polars as pl
from colored import attr, fg
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

logging.basicConfig(
    format="%(asctime)s %(levelname)-8s %(message)s",
    level=logging.INFO,
    datefmt="%Y-%m-%d %H:%M:%S",
)


class MyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, set):
            return list(obj)
        else:
            return super(MyEncoder, self).default(obj)


def import_config(config: str = "config/config.hjson", add: bool = False):
    with open(config, "r") as fp:
        config = hjson.load(fp)
    return config


def make_filepath(filepath: str) -> str:
    """
    Crée un chemin de fichier si celui-ci n'existe pas déjà.

    Cette fonction vérifie si le chemin de fichier spécifié existe déjà.
    Si ce n'est pas le cas, elle crée le chemin de fichier.

    Paramètres
    ----------
    filepath : str
        Le chemin de fichier à créer.

    Retourne
    -------
    str
        Le chemin de fichier spécifié.

    Notes
    -----
    La fonction utilise la bibliothèque os pour interagir avec le système d'exploitation.
    """

    if not os.path.exists(filepath):
        os.makedirs(filepath, exist_ok=True)
    return filepath


def import_datasets(
    datas: str,
    types: str,
    sep: str = ",",
) -> pd.DataFrame:
    """
    Importe des ensembles de données à l'aide de pandas ou polars.

    Parameters
    ----------
    datas : str
        Le chemin d'accès complet au fichier de données à importer.
    types : str
        Le type de bibliothèque à utiliser pour l'importation.
        Les options valides sont 'pandas', 'parquet' et 'polars'.
    sep : str, optional
        Le séparateur de colonnes à utiliser lors de l'importation du fichier.
        Par défaut, il s'agit d'une virgule (',').

    Returns
    -------
    pl.DataFrame
        Un DataFrame contenant les données importées.

    Raises
    ------
    ValueError
        Si le type spécifié n'est ni 'pandas', ni 'parquet', ni 'polars'.
    """
    data_name = datas.split("/")[-1]
    if types == "pandas":
        logging.info(
            f"{types.capitalize()} loaded ! Importing {data_name[:-4]}..."
        )
        return pd.read_csv(datas, sep=sep, low_memory=False)
    if types == "parquet":
        logging.info(
            f"{types.capitalize()} loaded ! Importing {data_name[:-8]}..."
        )
        return pd.read_parquet(datas)
    elif types == "polars":
        logging.info(
            f"{types.capitalize()} loaded ! Importing {data_name[:-4]}..."
        )
        return pl.read_csv(datas, separator=sep, ignore_errors=True)
    else:
        raise ValueError(
            f"{types} not recognize please use : [ pandas | polars ] "
        )


def order_and_rename(
    df: pd.DataFrame, og_col: list, new_col_name: list
) -> pd.DataFrame:
    """
    Ordonne et renomme les colonnes d'un DataFrame pandas.

    Paramètres
    ----------
    df : pd.DataFrame
        DataFrame d'entrée sur lequel effectuer les opérations.
    og_col : list
        Liste des noms originaux des colonnes à renommer.
    new_col_name : list
        Liste des nouveaux noms de colonnes.

    Retourne
    -------
    pd.DataFrame
        DataFrame avec les colonnes réorganisées et renommées.

    Notes
    -----
    Les listes og_col et new_col_name doivent avoir la même longueur.
    """
    rename_dict = {old: new for old, new in zip(og_col, new_col_name)}
    df.rename(columns=rename_dict, inplace=True)
    return df


def col_to_keep(datasets: str) -> list:
    """
    Renvoie une liste des noms de colonnes à conserver dans un dataframe en fonction du type de données.

    Parameters
    ----------
    datasets : str
        Le type de données pour lequel obtenir les noms de colonnes.
        Les valeurs valides sont "movies", "actors",
        "directors", "actors_movies" et "directors_movies".

    Returns
    -------
    list
        Une liste des noms de colonnes à conserver.

    Raises
    ------
    KeyError
        Si le type de données n'est pas valide.
    """
    if datasets == "movies":
        return [
            "tconst",
            "primaryTitle",
            "startYear",
            "runtimeMinutes",
            "genres",
            "averageRating",
            "numVotes",
        ]
    if datasets in ["actors", "directors"]:
        return [
            "nconst",
            "primaryName",
            "birthYear",
            "category",
            "knownForTitles",
            "ordering",
        ]
    if datasets in ["actors_movies", "directors_movies"]:
        return [
            "titre_id",
            "titre_str",
            "titre_date_sortie",
            "titre_duree",
            "titre_genres",
            "rating_avg",
            "rating_votes",
            "original_language",
            "original_title",
            "popularity",
            "production_countries",
            "revenue",
            "spoken_languages",
            "status",
            "region",
            "cuts",
            "nconst",
            "primaryName",
            "birthYear",
            "category",
            "characters",
            "knownForTitles",
            "ordering",
        ]
    if datasets == "machine_learning":
        return [
            "imdb_id",
            "title",
            "genres",
            "actors",
            "actors_ids",
            "director",
            "director_ids",
            "keywords",
            "id",
            "overview",
            "popularity",
            "release_date",
            "vote_average",
            "vote_count",
            "url",
            "image",
            "youtube",
        ]
    else:
        raise KeyError(f"{datasets} n'est pas valide!")


def col_renaming(datasets: str) -> list:
    """
    Fonction pour renvoyer une liste de noms de colonnes à modifier dans un dataframe.

    Paramètres
    ----------
    datasets : str
        Le nom du dataset pour lequel la liste des noms de colonnes est requise.

    Retourne
    -------
    list
        Une liste de noms de colonnes à modifier.
        Si le dataset est "movies", la liste contient les noms de colonnes
        spécifiques à ce dataset.
        Si le dataset est "actors_movies" ou "directors_movies", la liste contient les noms de
        colonnes spécifiques à ces datasets. Si le dataset n'est pas reconnu, une KeyError est levée.

    Lève
    -----
    KeyError
        Si le nom du dataset n'est pas reconnu.
    """
    if datasets == "movies":
        return [
            "titre_id",
            "titre_str",
            "titre_date_sortie",
            "titre_duree",
            "titre_genres",
            "rating_avg",
            "rating_votes",
        ]
    if datasets in ["actors_movies", "directors_movies"]:
        return [
            "titre_id",
            "titre_str",
            "titre_date_sortie",
            "titre_duree",
            "titre_genres",
            "rating_avg",
            "rating_votes",
            "original_language",
            "original_title",
            "popularity",
            "production_countries",
            "revenue",
            "spoken_languages",
            "status",
            "region",
            "cuts",
            "person_id",
            "person_name",
            "person_birthdate",
            "person_job",
            "person_role",
            "person_film",
            "person_index",
        ]
    if datasets == "machine_learning":
        return [
            "titre_id",
            "titre_str",
            "titre_genres",
            "actors",
            "actors_ids",
            "director",
            "director_ids",
            "keywords",
            "tmdb_id",
            "overview",
            "popularity",
            "date",
            "rating_avg",
            "rating_vote",
            "url",
            "image",
            "youtube",
        ]
    else:
        raise KeyError(f"{datasets} n'est pas valide!")


def color(text: str, color: str = None) -> str:
    if color and color.startswith("#"):
        return f"{fg(color)}{text}{attr(0)}"
    elif color == "red":
        return f"{fg(1)}{text}{attr(0)}"
    elif color == "green":
        return f"{fg(2)}{text}{attr(0)}"
    elif color == "yellow":
        return f"{fg(3)}{text}{attr(0)}"
    elif color == "blue":
        return f"{fg(4)}{text}{attr(0)}"
    else:
        return text


def clean_overview(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z]", " ", text)
    words = text.split()
    words = [w for w in words if w not in stopwords.words("french")]
    lemmatizer = WordNetLemmatizer()
    words = [lemmatizer.lemmatize(word) for word in words]
    return " ".join(words)


def supprimer_accents(texte: str) -> str:
    texte_clean = normalize("NFKD", texte)
    return "".join([c for c in texte_clean if not combining(c)])


def full_lower(text: str) -> str:
    return (
        text.replace(" ", "")
        .replace("-", "")
        .replace("'", "")
        .replace(":", "")
        .lower()
    )


def one_for_all(r):
    return (
        r["keywords"]
        + " "
        + r["actors"]
        + " "
        + r["director"]
        + " "
        + r["titre_genres"]
    )

def clean_dup(df: pd.DataFrame) -> pd.DataFrame:
    """
    Nettoie les doublons dans une colonne spécifique d'un DataFrame en ajoutant
    la date entre parenthèses.

    Parameters
    ----------
    df : pd.DataFrame
        Le DataFrame à nettoyer.

    Returns
    -------
    pd.DataFrame
        DataFrame avec les doublons nettoyés.
    """
    logging.info("Apply date to duplicated movies...")
    condi = df["titre_str"].duplicated(keep=False)
    df.loc[condi, "titre_str"] = (
        df.loc[condi, "titre_str"]
        + " "
        + "("
        + df.loc[condi, "date"].astype(str)
        + ")"
    )
    return df
