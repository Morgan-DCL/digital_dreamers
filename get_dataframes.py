import os
import pandas as pd

from tools import (
    ast,
    clean_overview,
    col_renaming,
    col_to_keep,
    color,
    full_lower,
    import_datasets,
    logging,
    make_filepath,
    one_for_all,
    order_and_rename,
    supprimer_accents,
)


class GetDataframes:
    """
    Classe pour gérer et manipuler les DataFrames.

    Attributs
    ----------
    config : dict
        Dictionnaire de configuration.
    default_path : str
        Chemin par défaut pour stocker les fichiers.
    download_path : str
        Chemin pour télécharger les fichiers.
    tsv_file : str
        Fichier TSV à traiter.

    Méthodes
    -------
    get_directors_movies_dataframe(modify: bool = False, cleaned: bool = False) -> pd.DataFrame:
        Récupère le DataFrame des films de réalisateurs, nettoyé ou non.

    get_dataframes(name: str, cleaned: bool = False) -> pd.DataFrame:
        Récupère le DataFrame demandé, nettoyé ou non.
    """

    def __init__(self, config: dict):
        self.config = config
        self.streamlit_path = make_filepath(config["path_streamlit"])
        self.fix_n = "\\N"

    def get_machine_learning_dataframe(
        self, cleaned: bool = False, modify: bool = False
    ) -> pd.DataFrame:
        name = "machine_learning"
        path_file = f"{self.streamlit_path}/{name}.parquet"
        name_og = "machine_learning_final"
        path_final_file = f"{self.streamlit_path}/{name_og}.parquet"

        if os.path.exists(path_final_file) and not modify:
            ml_df = import_datasets(path_final_file, "parquet")
            logging.info(f"Dataframe {name_og} ready to use!")
            return ml_df
        else:
            first_df = import_datasets(path_file, "parquet")
            ml_df = order_and_rename(
                first_df, col_to_keep(name), col_renaming(name)
            )
            to_clean = [
                "actors",
                "titre_genres",
                "director",
                "keywords",
            ]
            for t in to_clean:
                ml_df[t] = (
                    ml_df[t]
                    .apply(lambda x: ", ".join(map(str, x)))
                    .replace(" ", "")
                )
            ml_df["titre_clean"] = ml_df["titre_str"]
            ml_df["titre_clean"] = ml_df["titre_clean"].apply(
                lambda x: x.lower()
            )
            ml_df["date"] = pd.to_datetime(ml_df["date"])
            ml_df["date"] = ml_df["date"].dt.year
            clean_act_dct = ["actors_ids", "director_ids"]
            for act_dct in clean_act_dct:
                ml_df[act_dct] = ml_df[act_dct].apply(
                    lambda x: ast.literal_eval(x)
                )
            ml_df.reset_index(drop="index", inplace=True)
            ml_df.to_parquet(f"{self.streamlit_path}/site_web.parquet")

            logging.info("Cleaning StopWords and Lemmatize...")
            to_clean.extend(["titre_clean", "overview"])
            for col in to_clean:
                ml_df[col] = ml_df[col].astype(str).apply(supprimer_accents)
            ml_df["overview"] = (
                ml_df["overview"].astype(str).apply(clean_overview)
            )

            to_clean.remove("titre_clean")
            for t in to_clean:
                logging.info(f"lowering everything in {t}")
                ml_df[t] = ml_df[t].apply(full_lower)
            ml_df = ml_df[col_renaming(name) + ["titre_clean"]].copy()
            ml_df.reset_index(drop="index", inplace=True)
            ml_df.loc[:, "one_for_all"] = ml_df.apply(one_for_all, axis=1)
            ml_df.to_parquet(path_final_file)
        logging.info(f"Dataframe machine_learning_final ready to use!")
        return ml_df

    def get_dataframes(self, name: str, cleaned: bool = False) -> pd.DataFrame:
        """
        Récupère un DataFrame spécifique par son nom.

        Selon le nom donné, cette méthode charge ou crée le DataFrame
        correspondant, avec une option de nettoyage.

        Parameters
        ----------
        name : str
            Nom du DataFrame à récupérer.
        cleaned : bool, optional
            Indique si un nettoyage est requis (défaut False).

        Returns
        -------
        pd.DataFrame
            DataFrame demandé.
        """
        if name.lower() == "machine_learning":
            return self.get_machine_learning_dataframe(modify=cleaned)
        else:
            raise KeyError(f"{name.capitalize()} not know!")

    def get_all_dataframes(self):
        """
        Récupère tous les DataFrames principaux.

        Cette méthode parcourt une liste prédéfinie de noms de DataFrames
        et les charge ou les crée un par un. Elle utilise `get_dataframes`
        pour chaque type de DataFrame. Les opérations et leur achèvement
        sont enregistrés dans les logs.

        Chaque DataFrame est identifié par son nom et une couleur associée
        pour le logging. La méthode assure la création de DataFrames pour
        les films, films nettoyés, acteurs, réalisateurs, et données pour
        l'apprentissage machine.
        """
        names = (("machine_learning", "green"),)
        for name in names:
            txt = color(
                "-" * 10 + f" Start creating {name[0]} " + "-" * 10,
                color=name[1],
            )
            logging.info(txt)
            self.get_dataframes(name[0], True)
            txt = color(
                "-" * 10 + f" Job Done for {name[0]} ! " + "-" * 10 + "\n",
                color=name[1],
            )
            logging.info(txt)

        txt = color(
            "-" * 20
            + f" Job Done for {len(names)} dataframes ! "
            + "-" * 20
            + "\n",
            color="green",
        )
        logging.info(txt)
