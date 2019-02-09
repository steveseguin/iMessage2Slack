# iMessage2Slack
Forward iMessages from OSX to Slack -- use iMessage on Android!

Code is easy to modify -- extend it to work with SMS, email, and chatbots.

## dedicated to Aysha

requires Python3, Python SlackClient
```pip3 install slackclient```

Setup:
You will need to update the monitor.py file with a valid Slack API key; get that from Slack somewhere.

Just run with:
```python3 monitor.py```

Once running, it should push all new messages to your slack channel as they come in.

# notes
Doesn't work with images and such yet; needs more development to do that. Please feel free to contribute

iMessage on OSX needs to be working and setup for this to work -- this will be very hard to get working on a hackintosh as a result.

### example of output
![alt text](https://raw.githubusercontent.com/steveseguin/iMessage2Slack/master/example.png)
