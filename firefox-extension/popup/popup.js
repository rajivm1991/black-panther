const hidePage = `body > :not(.beastify-image) {
                    display: none;
                  }`;

function listenForClicks() {
    console.log('listening');
    document.addEventListener("click", (e) => {
        function beastNameToURL(beastName) {
            return beastName
        }

        function beastify(tabs) {
            browser.tabs.insertCSS({code: hidePage}).then(() => {
                let url = beastNameToURL(e.target.textContent);
                browser.tabs.sendMessage(tabs[0].id, {
                    command: "beastify",
                    beastURL: url
                });
            });
        }

        function reset(tabs) {
            browser.tabs.removeCSS({code: hidePage}).then(() => {
                browser.tabs.sendMessage(tabs[0].id, {
                    command: "reset",
                });
            });
        }

        function reportError(error) {
            console.error(`Could not beastify: ${error}`);
        }

        if (e.target.classList.contains("beast")) {
            browser.tabs.query({active: true, currentWindow: true})
                        .then(beastify)
                        .catch(reportError);
        } else if (e.target.classList.contains("reset")) {
            browser.tabs.query({active: true, currentWindow: true})
                        .then(reset)
                        .catch(reportError);
        }
    });
}

function reportExecuteScriptError(error) {
    document.querySelector("#popup-content").classList.add("hidden");
    document.querySelector("#error-content").classList.remove("hidden");
    console.error(`Failed to execute beastify content script: ${error.message}`);
}

browser.tabs.executeScript({file: "/content_scripts/beastify.js"})
            .then(listenForClicks)
            .catch(reportExecuteScriptError);