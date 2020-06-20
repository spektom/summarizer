function sendContent() {
  document.getElementsByClassName('reader-message')[0].remove();

  browser.runtime.sendMessage({
    'title': document.getElementsByClassName('reader-title')[0].innerText,
    'html': document.getElementsByClassName('container')[0].outerHTML
  });
}

function isContentLoaded() {
  let e = document.getElementsByClassName('reader-estimated-time');
  return e.length > 0 && e[0].innerText.length > 0;
}

function waitForContent(attempt) {
  if (attempt > 10 || isContentLoaded()) {
    setTimeout(sendContent, 3000);
  } else {
    setTimeout(waitForContent, 1000, attempt + 1);
  }
}

setTimeout(waitForContent, 1000, 0);
