
import csv
import re
import requests


def get_html(url):
  """ Returns the HTML of the url page """

  r = requests.get(url, headers={
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 11_1_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36'
  })
  html = r.text

  return html


def get_game_page_data(page_num, game_num, url, datum):
  """ Fetches HTML of a particular game page and parses data from it """

  html = get_html(url + '/details')
  lines = html.split('\n')
  print('\t[%d - %d] getting game details: %s' % (page_num, game_num, url))

  start_parse_additional_info = False
  start_parse_esrb_rating = False
  start_parse_developer = False
  start_parse_genres = False

  for line in lines:
    if '<div class="product_details">' in line:
      start_parse_additional_info = True
    elif '<th scope="row">Rating:</th>' in line and start_parse_additional_info:
      start_parse_esrb_rating = True
    elif '<td>' in line and start_parse_esrb_rating:
      datum['esrb_rating'] = line.split('<td>')[1].split('</td>')[0]
      start_parse_esrb_rating = False
    elif '<th scope="row">Developer:</th>' in line and start_parse_additional_info:
      start_parse_developer = True
    elif '<td>' in line and start_parse_developer:
      datum['developers'] = line.split('<td>')[1].split('</td>')[0].split(",")
      start_parse_developer = False
    elif '<th scope="row">Genre(s):</th>' in line and start_parse_additional_info:
      start_parse_genres = True
    elif '<td>' not in line and start_parse_genres:
      datum['genres'] = [x.strip() for x in line.split('</td>')[0].split(',')]
      start_parse_genres = False


def parse_html(page_num, base_url, html):
  """ Parses the input HTML for Pokemon Game ratings"""

  lines = html.split('\n')

  data = []
  start_parse_table = False
  start_parse_meta_score_title_platform = False
  start_parse_date = False

  game_num = 1

  for line in lines:
    if '<table class="credits company_credits">' in line:
      start_parse_table = True

    elif '<td class="title brief_metascore">' in line:
      start_parse_meta_score_title_platform = True
      datum = {}

    elif '<span class="metascore_w small game' in line and start_parse_meta_score_title_platform:
      meta_score_str = line.split('">')[1].split('</span>')[0]
      if (meta_score_str != 'tbd'):
        datum["meta_score"] = int(meta_score_str)

    elif '<a href="' in line and start_parse_meta_score_title_platform:
      datum['title'] = line.split('">')[1].split(' (')[0]
      datum['platform'] = line.split(' (')[1].split(')</a>')[0]
      datum['link'] = line.split('<a href="')[1].split('">')[0]
      get_game_page_data(page_num, game_num, base_url + datum['link'], datum)
      start_parse_meta_score_title_platform = False
      game_num = game_num + 1

    elif '<td class="year">' in line:
      start_parse_date = True

    elif start_parse_date:
      datum['date'] = line.strip()
      start_parse_date = False

    elif '<span class="data textscore' in line and start_parse_table:
      user_score_str = line.split('">')[1].split('</span>')[0]
      if user_score_str != 'tbd':
        datum['user_score'] = float(user_score_str)
      data.append(datum)

  return data


def write_csv(data):
  """ Writes a CSV file of the ratings data """

  with open('data.csv', 'w') as file:
    writer = csv.DictWriter(file, fieldnames=['meta_score', 'title', 'platform', 'date', 'user_score', 'link', 'esrb_rating', 'developers', 'genres'])
    writer.writeheader()
    for row in data:
      writer.writerow(row)


def main():
  base_url = 'https://www.metacritic.com/'
  game_list_url = 'https://www.metacritic.com/company/nintendo?filter-options=games&num_items=100&sort_options=date&page='
  num_pages = 11

  data = []

  for page_num in range(0, num_pages):
    url = game_list_url + str(page_num)
    html = get_html(url)
    print('Got HTML from %s. Parsing...' % url)

    page_data = parse_html(page_num + 1, base_url, html)
    print('Got %d game ratings\n' % len(page_data))

    data.extend(page_data)

  print('Writing data to CSV...\n')
  write_csv(data)

  print('Done!')


if __name__ == '__main__':
    main()