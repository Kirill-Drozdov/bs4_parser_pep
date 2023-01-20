from pathlib import Path

MAIN_DOC_URL = 'https://docs.python.org/3/'
PEPS_MAIN_URL = 'https://peps.python.org/'
BASE_DIR = Path(__file__).parent
DATETIME_FORMAT = '%Y-%m-%d_%H-%M-%S'

RESULTS_WHATS_NEW = [('Ссылка на статью', 'Заголовок', 'Редактор, Автор')]
RESULTS_LATEST_VERSIONS = [('Ссылка на документацию', 'Версия', 'Статус')]
RESULTS_PEP = [('Статус', 'Количество')]

DOWNLOADS_DIR = BASE_DIR / 'downloads'
RESULTS_DIR = BASE_DIR / 'results'

LOG_FORMAT = '"%(asctime)s - [%(levelname)s] - %(message)s"'
DT_FORMAT = '%d.%m.%Y %H:%M:%S'
LOG_DIR = BASE_DIR / 'logs'
LOG_FILE = LOG_DIR / 'parser.log'

EXPECTED_STATUS = {
    'A': ('Active', 'Accepted'),
    'D': ('Deferred',),
    'F': ('Final',),
    'P': ('Provisional',),
    'R': ('Rejected',),
    'S': ('Superseded',),
    'W': ('Withdrawn',),
    '': ('Draft', 'Active'),
}

PARSER_DESCRIPTION = 'Парсер документации Python'
PARSER_MODE_HELP = 'Режимы работы парсера'
PARSER_CLEAR_HELP = 'Очистка кеша'
PARSER_OUTPUT_HELP = 'Дополнительные способы вывода данных'
