# golfshot-downloader

This script downloads your GolfShot rounds and course scorecards into `data/rounds` and `data/courses` respectively. It utilizes the `json` model that GolfShot uses.

To download all your rounds, run:
```
python3 golfshot-downloader.py [USERNAME] [PASSWORD] [PROFILE_ID]
```

To download all your rounds until a specific one, run:
```
python3 golfshot-downloader.py [USERNAME] [PASSWORD] [PROFILE_ID] --until [ROUND_ID]
```