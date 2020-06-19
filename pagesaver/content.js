function sendContent(articleId) {
  document.getElementsByClassName("reader-message")[0].remove();

  browser.runtime.sendMessage({
    'id': articleId,
    'title': document.getElementsByClassName("reader-title")[0].innerText,
    'html': document.getElementsByClassName("container")[0].outerHTML
  });
}

function isContentLoaded() {
  return document.getElementsByClassName("reader-estimated-time")[0].innerText.length > 0;
}

function waitForContent(attempt, articleId) {
  if (attempt > 10 || isContentLoaded()) {
    setTimeout(sendContent, 3000, articleId);
  } else {
    setTimeout(waitForContent, 1000, attempt + 1, articleId);
  }
}

browser.runtime.onMessage.addListener(request => {
  waitForContent(0, request.articleId);
  return Promise.resolve();
});
