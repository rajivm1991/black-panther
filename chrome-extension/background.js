function postToBackend(data) {
    var form_data = new FormData();
    for (var key in data) {
        form_data.append(key, data[key]);
    }
    var xhr = new XMLHttpRequest();
    xhr.open('POST', 'http://localhost:5000/store/', true);
    xhr.onreadystatechange = function (oEvent) {
        if (this.readyState === 4) {
            console.log("xhr:", xhr);
            chrome.runtime.sendMessage({
                msg: "sentToBackend",
                status: this.status,
                statusText: this.statusText,
                responseText: this.responseText
            });
        }
    };
    xhr.send(form_data);
}

chrome.runtime.onMessage.addListener(function (request, sender, sendResponse) {
    console.log('onMessage');
    console.log(request.action);
    if (request.action === 'storePageSource') {
        chrome.tabs.query({active: true, currentWindow: true}, (tabs) => {
            var tab = tabs[0];
            console.log("url    :", tab.url);
            console.log("title  :", tab.title);
            console.log("window :", request.window);

            console.assert(typeof tab.url === 'string', 'tab.url should be a string');
            postToBackend({
                'url': tab.url,
                'title': tab.title,
                'page_source': request.source,
                'ips': request.ips,
                'window_width': request.window.width,
                'window_height': request.window.height
            })
        });
    }
});

// chrome.tabs.onActivated.addListener(function(activeInfo) {
//     console.log(activeInfo.tabId);
// });
