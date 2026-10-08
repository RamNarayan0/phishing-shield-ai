class BackendClient {
    static async verifyMessage(payload) {
        return new Promise((resolve, reject) => {
            chrome.runtime.sendMessage(
                { action: "VERIFY_MESSAGE", payload },
                (response) => {
                    if (chrome.runtime.lastError) {
                        reject(new Error(chrome.runtime.lastError.message));
                    } else if (!response.success) {
                        reject(new Error(response.error));
                    } else {
                        resolve(response.data);
                    }
                }
            );
        });
    }
}
window.BackendClient = BackendClient;
