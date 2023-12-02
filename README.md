```markdown
# DigitalDreamers Recommandation System

This repository contains the code for a movie recommendation system developed using Python and Streamlit.
The system recommends similar movies based on a machine learning model and user-selected preferences.

## Repository Content Overview

- `.gitignore`: Specifies intentionally untracked files to ignore
- `app.py`: The main application script for the Streamlit web app
- `requirements.txt`: A list of Python dependencies required for the project
- `start.py`: Script to initiate data fetching and DataFrame creation
- `update_movies.sh`: Shell script for updating movie data and pushing changes to Git
- `.streamlit/config.toml`: Configuration file for Streamlit app
- `config/config.hjson`: Configuration file in HJSON format with API keys and other settings
- `get_dataframes/api_tmdb.py`: Python script to fetch movie details from TMdb API
- `get_dataframes/get_dataframes.py`: Python script to manage and manipulate DataFrames
- `pages/full_bio.py`: Streamlit page script for displaying full actor/director biographies
- `utils/tools.py`: Utility functions used throughout the project
- `utils/tools_app.py`: Utility functions specific to the Streamlit app

## Features

- Movie recommendations based on user input
- Detailed movie information including synopsis, cast, and trailers
- Actor and director biographies with filmography
- Support for multiple languages
- Data fetching and processing from TMdb API

## Usage

To run the DigitalDreamers Recommandation System locally, you must have Python installed on your machine.

1. Clone the repository to your local machine.
2. Install the required dependencies using `pip`:

   ```bash
   pip install -r requirements.txt
   ```

3. Run the Streamlit application:

   ```bash
   streamlit run app.py
   ```

4. The web application should now be accessible in your browser.

## Contributing

If you would like to contribute to the project, please follow these steps:

1. Fork the repository and create your feature branch.
2. Make your changes and commit them with a clear commit message.
3. Push your changes and open a pull request for review.

Please ensure you adhere to the existing coding style and add unit tests for any new functionality.

## License

This project is open source and available under the [MIT License](LICENSE).

## Acknowledgments

- TMdb API: For providing access to their extensive movie database
- Streamlit: For the powerful and easy-to-use web application framework
- Contributors: For their valuable contributions to the project

## Contact
   ```bash
   morgan.leitao@gmail.com
   ```

For any questions or suggestions, please open an issue on the GitHub repository, and a maintainer will get back to you.
```
