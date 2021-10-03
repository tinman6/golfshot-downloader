#!/usr/bin/python

import argparse
from bs4 import BeautifulSoup
from html.parser import HTMLParser
import json
import re
import requests

GOLFSHOT_URL = 'https://play.golfshot.com'


class RoundParser(HTMLParser):
  def handle_data(self, data):
    # the golfshot model is available in a script block
    if 'Golfshot.Applications.Scorecard' in data:
      model = re.search(r"(?<=ReactDOM.hydrate\(React.createElement\(Golfshot.Applications.Scorecard, )(.*)(?=\), document.getElementById)", data).group()
      self.results = json.loads(model)


class CourseParser(HTMLParser):
  def handle_data(self, data):
    if 'Golfshot.Applications.CourseScorecard' in data:
      model = re.search(r'(?<=ReactDOM.hydrate\(React.createElement\(Golfshot.Applications.CourseScorecard, )(.*)(?=\), document.getElementById)', data).group()
      self.results = json.loads(model)


def download_course(session, course_id):
  COURSE_URL = f'{GOLFSHOT_URL}/courses/{course_id}'

  res = session.get(COURSE_URL)
  p = CourseParser()
  p.feed(res.text)

  course_uuid = p.results['source'].split('/')[-2]
  scorecard = session.get(p.results['source']).json()['scorecard']  # remove unused siblings

  with open('data/courses/%s.json' % course_id, 'w') as f:
    ret = {'courseId': course_id,
           'courseUuid': course_uuid,
           'scorecard': scorecard}
    json.dump(ret, f)


def download_round(session, profile_id, round_id):
  ROUND_URL = f'{GOLFSHOT_URL}/profiles/{profile_id}/rounds/{round_id}'

  res = session.get(ROUND_URL)
  p = RoundParser()
  p.feed(res.text)
  with open('data/rounds/%s.json' % p.results['roundGroupId'], 'w') as f:
    json.dump(p.results, f)

  download_course(session, p.results['model']['detail']['golfCourseWebId'])


def download_rounds(session, profile_id, last_round=None):
  ROUNDS_URL = f'{GOLFSHOT_URL}/profiles/{profile_id}/rounds'
  params = {'sb': 'Date', 'sd': 'Descending', 'p': 1}

  download_rounds = True
  while download_rounds:
    rounds_html = session.get(ROUNDS_URL, data=params).text
    soup = BeautifulSoup(rounds_html, 'html.parser')
    round_table = soup.find('table', {'class': 'search-results'})

    if not round_table:
      download_rounds = False
      break

    for row in round_table.tbody.findAll('tr'):
      round_id = row.attrs['data-href'].split('/')[-1]
      if round_id == last_round:
        download_rounds = False
        break
      download_round(session, profile_id, round_id)

    params['p'] += 1





parser = argparse.ArgumentParser(description='Download GolfShot data')
parser.add_argument('username', help='Username for GolfShot account')
parser.add_argument('password', help='Password for GolfShot account')
parser.add_argument('profile_id', help='Profile ID for GolfShot account')
parser.add_argument('--until', help='Download rounds until specified round (by descending date)')
args = parser.parse_args()

with requests.Session() as session:
  signin = session.post(f'{GOLFSHOT_URL}/signin',
                        data={'Email': args.username,
                              'Password': args.password})
  download_rounds(session, args.profile_id, args.until)
