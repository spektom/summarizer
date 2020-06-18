setInterval(processNextTask, 10000);

function fetchNextTask(callback) {
  function reqListener() {
    if (this.status == 200) {
      task = JSON.parse(this.responseText);
      callback(task);
    } else {
      console.error(this.responseText);
    }
  }

  var req = new XMLHttpRequest();
  req.addEventListener('load', reqListener);
  req.open('GET', 'http://localhost:5000/tasks/next?' + new Date().getTime());
  req.send();
}

function sendTaskUpdate(task) {
  function reqListener() {
    if (this.status != 200) {
      console.error(this.responseText);
    }
  }

  var req = new XMLHttpRequest();
  req.addEventListener('load', reqListener);
  req.open('POST', 'http://localhost:5000/tasks/update');
  req.setRequestHeader('Content-Type', 'application/json;charset=UTF-8');
  req.send(JSON.stringify(task));
}

function onTabOpen(tab) {
  browser.tabs.executeScript(tab.id, {
    file: 'content.js'
  }).catch(console.error);
}

function processNextTask() {
  fetchNextTask(function(task) {
    browser.tabs.create({
      openInReaderMode: true,
      url: task.uri
    }).then(onTabOpen, console.error);
  });
}

function onContentReceived(content, sender) {
  sendTaskUpdate({'content': content.html});
  browser.tabs.remove(sender.tab.id);
}

browser.runtime.onMessage.addListener(onContentReceived);
