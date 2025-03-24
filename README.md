# CyberSierra Chatbot

CyberSierra Chatbot is a Streamlit-based chatbot powered by OpenAI and PandasAI, designed to analyze uploaded CSV or Excel files and provide insights based on user queries.

## Requirements

- Python 3.11

## Installation

1. Clone the repository:
   ```sh
   git clone <repository-url>
   cd <repository-folder>
   ```
2. Create a virtual environment (recommended):
   ```sh
   python3.11 -m venv myenv
   source myenv/bin/activate  # On Windows, use: myenv\Scripts\activate
   ```
3. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```

## Dependencies

The following dependencies are required:
- `openai`
- `python-dotenv`
- `streamlit`
- `pandasai`
- `pandas`
- `pandasai-openai`

You can install them manually using:
```sh
pip install python-dotenv streamlit pandasai pandas pandasai-openai xlrd
```

## Environment Variables

Before running the application, set up an `.env` file in the project directory with the following key:

```sh
OPENAI_API_KEY=<your_openai_api_key>
```

## Usage

Run the Streamlit application:
```sh
streamlit run app.py
```

## Features

- Upload CSV or Excel files.
- View a preview of the uploaded data.
- Chat with the AI to analyze and gain insights from the data.
- Powered by OpenAI for intelligent data analysis.

## Folder Structure

```
├── data/             # Stores uploaded files
├── myenv/            # Virtual environment (optional)
├── .env              # API keys and environment variables
├── requirements.txt  # Required dependencies
├── app.py            # Main application script
├── README.md         # Project documentation
```

## Notes

- Ensure that you have a valid OpenAI API key before running the application.
- The application creates a `data/` directory to store uploaded files automatically.

## License

MIT License

