#!/usr/bin/python

from html.parser import HTMLParser
import json
import requests
import pprint


class ScorecardParser(HTMLParser):
  def handle_data(self, data):
    if data.startswith('ReactDOM.hydrate(React.createElement(Golfshot.Applications.Scorecard,'):
      # the golfshot model is available in a script block
      model = json.loads(data.partition('\n')[0][70:-57])  # counting chars is not great, but simpliest
      self.results = model


with open('mocks/scorecard.html') as mock_scorecard:
  p = ScorecardParser()
  p.feed(mock_scorecard.read())
  pprint.pprint(p.results)
