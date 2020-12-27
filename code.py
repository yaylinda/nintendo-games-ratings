
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


def parse_html(html):
  """ Parses the input HTML for Pokemon Game ratings"""

  lines = html.split('\n')

  data = []
  start_parse_table = False
  start_parse_meta_score_title_platform = False
  start_parse_date = False

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
      start_parse_meta_score_title_platform = False

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
    writer = csv.DictWriter(file, fieldnames=['meta_score', 'title', 'platform', 'date', 'user_score'])
    writer.writeheader()
    for row in data:
      writer.writerow(row)


def main():
  base_url = 'https://www.metacritic.com/company/nintendo?filter-options=games&num_items=100&sort_options=date&page='
  num_pages = 11

  data = []

  for page_num in range(0, num_pages):
    url = base_url + str(page_num)
    html = get_html(url)
    print('Got HTML from %s. Parsing...' % url)

    page_data = parse_html(html)
    print('Got %d game ratings\n' % len(page_data))

    data.extend(page_data)

  print('Writing data to CSV...\n')
  write_csv(data)

  print('Done!')


if __name__ == '__main__':
    main()