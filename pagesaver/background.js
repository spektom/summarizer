setInterval(processNextUri, 30000);

let tabStates = {};

function fetchNextUri(callback) {
  function reqListener() {
    if (this.status === 200) {
      let response = JSON.parse(this.responseText);
      callback(response.uri, response.id);
    } else if (this.status > 204) {
      console.error(this.statusText);
    }
  }

  let req = new XMLHttpRequest();
  req.addEventListener('load', reqListener);
  req.open('GET', 'http://localhost:5000/nexturi?_t=' + new Date().getTime());
  req.send();
}

function sendArticleUpdate(content) {
  function reqListener() {
    if (this.status !== 200) {
      console.error(this.statusText);
    }
  }

  let req = new XMLHttpRequest();
  req.addEventListener('load', reqListener);
  req.open('POST', 'http://localhost:5000/articles/update');
  req.setRequestHeader('Content-Type', 'application/json;charset=UTF-8');
  req.send(JSON.stringify(content));
}

function processNextUri() {
  fetchNextUri((uri, articleId) => {
    console.log(`Received new URI to process: ${uri}`);
    browser.tabs.create({
      url: uri
    }).then((tab) => {
      console.log(`Tab ${tab.id} created`);
      tabStates[tab.id] = {
        state: 'created',
        articleId: articleId
      };
    }, console.error);
  });
}

function onTabUpdated(tabId, changeInfo, tabInfo) {
  function onError(error) {
    console.error(error);
    delete tabStates[tabId];
    browser.tabs.remove(tabId);
  }

  let tabState = tabStates[tabId];
  if (typeof(tabState) !== 'undefined' && changeInfo.status === 'complete') {
    if (tabState.state === 'in-reader') {
      tabState.state = 'loaded';
      console.log(`Tab ${tabId} is in reader mode now, injecting content script`);
      browser.tabs.executeScript(tabId, {
        file: 'content.js'
      }).catch(onError);
    }
    if (tabState.state === 'created') {
      tabState.state = 'in-reader';
      console.log(`Tab ${tabId} is loaded, toggling reader mode`);
      browser.tabs.toggleReaderMode(tabId).catch(onError);
    }
  }
}

function onContentReceived(content, sender) {
  tabId = sender.tab.id;
  console.log(`Content received from tab ${tabId}`);
  content.id = tabStates[tabId].articleId;
  delete tabStates[tabId];
  browser.tabs.remove(tabId);
  sendArticleUpdate(content);
}

browser.tabs.onUpdated.addListener(onTabUpdated);
browser.runtime.onMessage.addListener(onContentReceived);
