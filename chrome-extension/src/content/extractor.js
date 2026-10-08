class Extractor {
    static extractVisibleText() {
        return document.body.innerText;
    }
    
    static extractUrls() {
        const links = document.querySelectorAll('a');
        const urls = [];
        links.forEach(link => {
            if (link.href && link.href.startsWith('http')) {
                urls.push(link.href);
            }
        });
        return [...new Set(urls)]; // unique
    }
}
window.Extractor = Extractor;
