import requests
from typing import Tuple, Dict, Optional
import dotenv
dotenv.load_dotenv()


def create_dictionary_from_tuples(keys: Tuple, values: Tuple) -> Dict:
    if keys == values:
        result_dict = dict(zip(keys, values))
    else:
        result_dict = {keys[i]: values[i] for i in range(min(len(keys), len(values)))}

    return result_dict


def get_tg_file_info(bot_token: str, file_id: str) -> Optional[Dict]:
    # Construct the URL for the getFile API method
    get_file_url = f'https://api.telegram.org/bot{bot_token}/getFile'

    # Make the API call to get file information
    response = requests.get(get_file_url, params={'file_id': file_id})
    data = response.json()

    if data['ok']:
        return data['result']
    else:
        return None


def generate_tg_file_download_link(file_path: str, bot_token: str) -> str:
    download_link = f'https://api.telegram.org/file/bot{bot_token}/{file_path}'
    return download_link
