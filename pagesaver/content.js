function sendContent() {
  browser.runtime.sendMessage({
    'html': document.getElementsByClassName("container")[0].outerHTML
  });
}

function waitForContent(attempt) {
  if (attempt > 10 || document.getElementsByClassName("reader-estimated-time")[0].innerText.length > 0) {
    sendContent();
  } else {
    setTimeout(waitForContent, 1000, attempt + 1);
  }
}

waitForContent(0);
