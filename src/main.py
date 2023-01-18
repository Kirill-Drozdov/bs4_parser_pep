import re
import requests_cache
import logging
from urllib.parse import urljoin


from bs4 import BeautifulSoup
from tqdm import tqdm

from constants import BASE_DIR, EXPECTED_STATUS, MAIN_DOC_URL, PEPS_MAIN_URL
from configs import (
    configure_argument_parser,
    configure_logging
)
from outputs import control_output
from utils import get_response, find_tag


def whats_new(session):
    whats_new_url = urljoin(MAIN_DOC_URL, 'whatsnew/')
    response = get_response(session, whats_new_url)
    soup = BeautifulSoup(response.text, features='lxml')

    main_div = find_tag(soup, 'section', attrs={'id': 'what-s-new-in-python'})
    div_with_ul = find_tag(main_div, 'div', attrs={'class': 'toctree-wrapper'})

    sections_by_python = div_with_ul.find_all(
        'li', attrs={'class': 'toctree-l1'}
    )

    results = [('Ссылка на статью', 'Заголовок', 'Редактор, Автор')]
    for section in tqdm(sections_by_python):
        version_a_tag = find_tag(section, 'a')
        version_link = urljoin(whats_new_url, version_a_tag['href'])

        response = get_response(session, version_link)
        soup = BeautifulSoup(response.text, 'lxml')

        h1 = find_tag(soup, 'h1')
        dl = find_tag(soup, 'dl')
        dl_text = dl.text.replace('\n', ' ')
        results.append(
            (version_link, h1.text, dl_text)
        )
    return results


def latest_versions(session):
    response = get_response(session, MAIN_DOC_URL)
    soup = BeautifulSoup(response.text, features='lxml')

    sidebar = find_tag(soup, 'div', attrs={'class': 'sphinxsidebarwrapper'})
    ul_tags = sidebar.find_all('ul')

    for ul in ul_tags:
        if 'All versions' in ul.text:
            a_tags = ul.find_all('a')
            break
        else:
            raise Exception('Ничего не нашлось')

    results = [('Ссылка на документацию', 'Версия', 'Статус')]
    pattern = r'Python (?P<version>\d\.\d+) \((?P<status>.*)\)'

    for a_tag in tqdm(a_tags):
        link = a_tag['href']
        text_match = re.search(pattern, a_tag.text)
        try:
            version = text_match.group('version')
            status = text_match.group('status')
        except AttributeError:
            version, status = a_tag.text, ''
        results.append((link, version, status))

    return results


def download(session):
    downloads_url = urljoin(MAIN_DOC_URL, 'download.html')
    response = get_response(session, downloads_url)
    soup = BeautifulSoup(response.text, features='lxml')

    table_tag = find_tag(soup, 'table', attrs={'class': 'docutils'})
    pdf_a4_tag = find_tag(
        table_tag, 'a', {'href': re.compile(r'.+pdf-a4\.zip$')}
    )
    pdf_a4_link = pdf_a4_tag['href']
    archive_url = urljoin(downloads_url, pdf_a4_link)
    filename = archive_url.split('/')[-1]
    downloads_dir = BASE_DIR / 'downloads'
    downloads_dir.mkdir(exist_ok=True)
    archive_path = downloads_dir / filename

    response = get_response(session, archive_url)

    with open(archive_path, 'wb') as file:
        file.write(response.content)
    logging.info(f'Архив был загружен и сохранён: {archive_path}')


def pep(session):
    response = get_response(session, PEPS_MAIN_URL)
    soup = BeautifulSoup(response.text, features='lxml')

    numerical_index = find_tag(
        soup, 'section', attrs={'id': 'numerical-index'}
    )
    tbody_tag = find_tag(numerical_index, 'tbody')
    tr_tags = tbody_tag.find_all('tr')

    status_count = {
        'Active': 0,
        'Accepted': 0,
        'Deferred': 0,
        'Final': 0,
        'Provisional': 0,
        'Rejected': 0,
        'Superseded': 0,
        'Withdrawn': 0,
        'Draft': 0,
    }
    count = 0
    output = [('Статус', 'Количество')]
    for tr in tr_tags:
        count += 1
        preview_status = find_tag(tr, 'abbr').text[1:]
        parse_status = EXPECTED_STATUS[preview_status]
        a_tag = find_tag(tr, 'a')
        link = a_tag['href']
        pep_detail_url = urljoin(PEPS_MAIN_URL, link)
        response = get_response(session, pep_detail_url)
        soup = BeautifulSoup(response.text, features='lxml')
        section_tag = find_tag(soup, 'section', attrs={'id': 'pep-content'})
        dt_tag = section_tag.dl.find_all('dt')

        for dt in dt_tag:
            if dt.text == 'Status:':
                status_detail = dt.next_sibling.next_sibling.text
                break

        try:
            status_count[status_detail] += 1
        except KeyError:
            logging.info(f'Указан несуществующий статус: {status_detail}')

        if parse_status[0] != status_detail:
            message = (
                f'\nСтатусы не совпадают! - {pep_detail_url}\nСтатус в карточке: {status_detail}\n'
                f'Ожидаемые статусы: {parse_status}'
            )
            if len(parse_status) < 2:
                logging.info(message)
            elif parse_status[1] != status_detail:
                logging.info(message)

    for status, count_status in status_count.items():
        output.append((status, count_status))

    output.append(('Total', count))
    return output


MODE_TO_FUNCTION = {
    'whats-new': whats_new,
    'latest-versions': latest_versions,
    'download': download,
    'pep': pep,
}


def main():
    configure_logging()
    logging.info('Парсер запущен!')

    arg_parser = configure_argument_parser(MODE_TO_FUNCTION.keys())
    args = arg_parser.parse_args()
    logging.info(f'Аргументы командной строки: {args}')

    session = requests_cache.CachedSession()
    if args.clear_cache:
        session.cache.clear()

    parser_mode = args.mode
    results = MODE_TO_FUNCTION[parser_mode](session)

    if results is not None:
        control_output(results, args)
    logging.info('Парсер завершил работу.')


if __name__ == '__main__':
    main()
