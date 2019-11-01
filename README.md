# Strawpoll Bot

![](https://img.shields.io/badge/license-GPLv2-blue)

## Requirements:
- Python 2 or 3
- `pip install requests`

## Script Arguments:
- **id:** The strawpoll.me Poll ID
- **option:** Which option should the bots vote for? 1 for first checkbox, 2 for second, etc ...
- **f F:** Change the frequency of the votes (one every F ms)
- **m M:** Max M threads
- **p:** Use proxies (in case the poll is doing an IP Check)

![](/img/help.png)

## Limitations:
- It cannot vote for multiple options at once
- It cannot vote for polls with a captcha

## Demo:
![](/img/demo.png)
