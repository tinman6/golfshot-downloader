#!/usr/bin/python

import argparse
from html.parser import HTMLParser
import json
import re
import requests


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


def download_round(url, session):
  res = session.get(url)
  p = RoundParser()
  p.feed(res.text)
  with open('data/rounds/%s.json' % p.results['roundGroupId'], 'w') as f:
    json.dump(p.results, f)


def download_course(url, session):
  res = session.get(url)
  p = CourseParser()
  p.feed(res.text)

  course_id = url.split('/')[-1]
  course_uuid = p.results['source'].split('/')[-2]
  scorecard = session.get(p.results['source']).json()['scorecard']  # remove unused siblings

  with open('data/courses/%s.json' % course_id, 'w') as f:
    ret = {'courseId': course_id,
           'courseUuid': course_uuid,
           'scorecard': scorecard}
    json.dump(ret, f)





parser = argparse.ArgumentParser(description='Download GolfShot data')
parser.add_argument('username', help='Username for GolfShot account')
parser.add_argument('password', help='Password for GolfShot account')
args = parser.parse_args()


GOLFSHOT_URL = 'https://play.golfshot.com'

with requests.Session() as session:
  signin = session.post('%s/signin' % GOLFSHOT_URL,
                        data={'Email': args.username,
                              'Password': args.password})

  download_round('ROUND_URL', session)
  download_course('COURSE_URL', session)
