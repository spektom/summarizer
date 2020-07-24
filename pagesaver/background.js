let managerUri = 'http://localhost:5000';
let maxTasks = 5;
let taskFetchIntervalSecs = 20;
let taskContexts = {};

function xhrGet(uri, callback) {
  let xhr = new XMLHttpRequest();
  xhr.onload = () => {
    callback(xhr);
  }
  xhr.timeout = 2000;
  xhr.open('GET', uri);
  xhr.send();
}

function xhrPost(uri, content, callback) {
  let xhr = new XMLHttpRequest();
  xhr.onload = () => {
    callback(xhr);
  }
  xhr.timeout = 2000;
  xhr.open('POST', uri);
  xhr.setRequestHeader('Content-Type', 'application/json;charset=UTF-8');
  xhr.send(JSON.stringify(content));
}

function fetchNextUri(callback) {
  xhrGet(`${managerUri}/tasks/next`, (xhr) => {
    if (xhr.status === 200) {
      let article = JSON.parse(xhr.responseText);
      callback(article.uri, article.id);
    } else if (xhr.status > 204) {
      console.error(xhr.statusText);
    }
  });
}

function sendContent(articleId, content) {
  xhrPost(`${managerUri}/article/${articleId}`, content, (xhr) => {
    if (xhr.status !== 200) {
      console.error(xhr.statusText);
    }
  });
}

function log(message, level) {
  if (!level) level = 'INFO';
  xhrPost(`${managerUri}/pagesaver/log`, {
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

function createTaskContext(tabId, articleId) {
  taskContexts[tabId] = {
    state: 'created',
    articleId: articleId,
    createdOnMillis: new Date().getTime(),
    dispose: () => {
      delete taskContexts[tabId];
      browser.tabs.remove(tabId);
    }
  };
}

function cleanStaleTaskContexts() {
  let nowMillis = new Date().getTime();
  Object.values(taskContexts).forEach((taskContext) => {
    if (taskContext.createdOnMillis + 100000 > nowMillis) {
      taskContext.dispose()
    }
  });
}

function processNextUri() {
  if (Object.keys(taskContexts).length >= maxTasks) {
    log(`Max number of tabs (${maxTasks}) is open already`, 'WARN');
    cleanStaleTaskContexts();
  } else {
    fetchNextUri((uri, articleId) => {
      log(`Received article #${articleId} to process: ${uri}`);
      browser.tabs.create({
        url: uri
      }).then((tab) => {
        log(`Tab #${tab.id} created for article #${articleId}`);
        createTaskContext(tab.id, articleId);
      }, logError);
    });
  }
}

function onTabUpdated(tabId, changeInfo, tab) {
  let taskContext = taskContexts[tabId];

  function onError(error) {
    taskContext.dispose();
    logError(error);
  }

  // State machine depending on current tab state:
  if (typeof(taskContext) !== 'undefined' && changeInfo.status === 'complete') {
    if (taskContext.state === 'created') {
      taskContext.state = 'in-reader';
      if (tab.isArticle) {
        log(`Tab #${tabId} is loaded, toggling reader mode`);
        browser.tabs.toggleReaderMode(tabId).catch(onError);
      } else {
        onError(`Tab #${tabId} is loaded, but it doesn't seem to be an article: ${tab.url}`);
      }
    } else if (taskContext.state === 'in-reader') {
      taskContext.state = 'loaded';
      log(`Tab #${tabId} is in reader mode now, injecting content script`);
      browser.tabs.executeScript(tabId, {
        file: 'content.js'
      }).catch(onError);
    }
  }
}

function onContentReceived(content, sender) {
  tabId = sender.tab.id;
  let taskContext = taskContexts[tabId];
  log(`Article #${taskContext.articleId} content received from tab #${tabId}`);
  taskContext.dispose();
  sendContent(taskContext.articleId, content);
}

browser.tabs.onUpdated.addListener(onTabUpdated);
browser.runtime.onMessage.addListener(onContentReceived);

setInterval(processNextUri, taskFetchIntervalSecs * 1000);
