# Report system

Generates reports about system state using scenarios

Scenarios uses plugins to do things

Used database migration project - https://gitlab.app.ipl/db/mon.celery/commits/develop

Requires headless firefox (https://medium.com/@griggheo/running-selenium-webdriver-tests-using-firefox-headless-mode-on-ubuntu-d32500bb6af2):

```
apt install firefox xvfb
Xvfb :10 -ac &
DISPLAY=:10 firefox
```

Also for selenium geckodriver must be used - https://askubuntu.com/questions/870530/how-to-install-geckodriver-in-ubuntu
