setInterval(processNextUri, 10000);

function fetchNextUri(callback) {
  function reqListener() {
    if (this.status == 200) {
      response = JSON.parse(this.responseText);
      callback(response.uri, response.id);
    } else if (this.status > 204) {
      console.error(this.statusText);
    }
  }

  var req = new XMLHttpRequest();
  req.addEventListener('load', reqListener);
  req.open('GET', 'http://localhost:5000/nexturi?_t=' + new Date().getTime());
  req.send();

}

function sendArticleUpdate(content) {
  function reqListener() {
    if (this.status != 200) {
      console.error(this.statusText);
    }
  }

  var req = new XMLHttpRequest();
  req.addEventListener('load', reqListener);
  req.open('POST', 'http://localhost:5000/articles/update');
  req.setRequestHeader('Content-Type', 'application/json;charset=UTF-8');
  req.send(JSON.stringify(content));
}

function requestContent(tab, articleId) {
  function onError(error) {
    console.error(error);
    browser.tabs.remove(tab.id);
  }

  browser.tabs.executeScript(tab.id, {
    file: 'content.js'
  }).then(() => {
    browser.tabs.sendMessage(tab.id, articleId).catch(onError);
  }, onError);
}

function processNextUri() {
  fetchNextUri((uri, articleId) => {
    browser.tabs.create({
      openInReaderMode: true,
      url: uri
    }).then((tab) => {
      requestContent(tab, {
        articleId: articleId
      });
    }, console.error);
  });
}

function onContentReceived(content, sender) {
  sendArticleUpdate(content);
  browser.tabs.remove(sender.tab.id);
}

browser.runtime.onMessage.addListener(onContentReceived);
