#!/usr/bin/python

from html.parser import HTMLParser
import json
import requests
import pprint


class ScorecardParser(HTMLParser):
  def handle_data(self, data):
    # the golfshot model is available in a script block
    if 'Golfshot.Applications.Scorecard' in data:
      for line in data.splitlines():
        if 'Golfshot.Applications.Scorecard' in line:
          # counting chars is not great, but simpliest
          model = json.loads(line[70:-57])
          self.results = model


class CourseParser(HTMLParser):
  def handle_data(self, data):
    if 'Golfshot.Applications.CourseScorecard' in data:
      for line in data.splitlines():
        if 'Golfshot.Applications.CourseScorecard' in line:
          model = json.loads(line[76:-59])
          self.results = model


with open('mocks/scorecard.html') as mock_scorecard:
  p = ScorecardParser()
  p.feed(mock_scorecard.read())
  pprint.pprint(p.results)


with open('mocks/course.html') as mock_course:
  p = CourseParser()
  p.feed(mock_course.read())
  pprint.pprint(p.results)
