let managerUri = 'http://localhost:5000';
let maxOpenTabs = 5;
let newTaskFetchIntervalSecs = 10;
let tabStates = {}; // holds global state of open tabs, their respective article ID, etc.

function managerGet(api, callback) {
  let xhr = new XMLHttpRequest();
  xhr.onload = () => {
    callback(xhr);
  }
  xhr.open('GET', managerUri + api);
  xhr.send();
}

function managerPost(api, content, callback) {
  let xhr = new XMLHttpRequest();
  xhr.onload = () => {
    callback(xhr);
  }
  xhr.open('POST', managerUri + api);
  xhr.setRequestHeader('Content-Type', 'application/json;charset=UTF-8');
  xhr.send(JSON.stringify(content));
}

function fetchNextUri(callback) {
  managerGet('/tasks/next', (xhr) => {
    if (xhr.status === 200) {
      let article = JSON.parse(xhr.responseText);
      callback(article.uri, article.id);
    } else if (xhr.status > 204) {
      console.error(xhr.statusText);
    }
  });
}

function sendArticleUpdate(content) {
  managerPost('/articles/update', content, (xhr) => {
    if (xhr.status !== 200) {
      console.error(xhr.statusText);
    }
  });
}

function log(message, level) {
  if (!level) level = 'INFO';
  managerPost('/pagesaver/log', {
    level: level,
    message: message,
    ts: new Date().toISOString()
  }, (xhr) => {
    if (xhr.status !== 200) {
      console.error(xhr.statusText);
    }
  });
}

function logError(error) {
  log(error, 'ERROR');
}

function processNextUri() {
  if (Object.keys(tabStates).length >= maxOpenTabs) {
    log(`Max number of tabs (${maxOpenTabs}) is open already`, 'WARN');
  } else {
    fetchNextUri((uri, articleId) => {
      log(`Received new URI to process: ${uri}`);
      browser.tabs.create({
        url: uri
      }).then((tab) => {
        log(`Tab #${tab.id} created for article #${articleId}`);
        tabStates[tab.id] = {
          state: 'created',
          articleId: articleId
        };
      }, logError);
    });
  }
}

function onTabUpdated(tabId, changeInfo, tab) {
  function onError(error) {
    delete tabStates[tabId];
    browser.tabs.remove(tabId);
    logError(error);
  }

  let tabState = tabStates[tabId];

  // State machine depending on current tab state:
  if (typeof(tabState) !== 'undefined' && changeInfo.status === 'complete') {
    if (tabState.state === 'created') {
      tabState.state = 'in-reader';
      if (tab.isArticle) {
        // Switch to reader mode
        log(`Tab #${tabId} is loaded, toggling reader mode`);
        browser.tabs.toggleReaderMode(tabId).catch(onError);
      } else {
        // Not an article
        onError(`Tab #${tabId} is loaded, but it doesn't seem to be an article: ${tab.url}`);
      }
    } else if (tabState.state === 'in-reader') {
      // Finished content retrieval
      tabState.state = 'loaded';
      log(`Tab #${tabId} is in reader mode now, injecting content script`);
      browser.tabs.executeScript(tabId, {
        file: 'content.js'
      }).catch(onError);
    }
  }
}

function onContentReceived(content, sender) {
  tabId = sender.tab.id;
  log(`Content received from tab ${tabId}`);
  content.id = tabStates[tabId].articleId;
  delete tabStates[tabId];
  browser.tabs.remove(tabId);
  sendArticleUpdate(content);
}

browser.tabs.onUpdated.addListener(onTabUpdated);
browser.runtime.onMessage.addListener(onContentReceived);

setInterval(processNextUri, newTaskFetchIntervalSecs * 1000);
