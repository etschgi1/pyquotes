const quoteSeperator = '^----$';
const authorSeperator = '^\s{4}(.*?)$';
const quoteFileAddress = 'quotes.txt';

const quoteBodyHTMLElement = 'quote-body';
const fromHTMLElement = 'from';


class Quotes {
  htmlFields = { quoteBody: null, from: null };

  constructor() {
    this.htmlFields.quoteBody = document.getElementById(quoteBodyHTMLElement);
    this.htmlFields.from = document.getElementById(fromHTMLElement);

    this.getFile();
  }

  async getFile() {
    let content;
    const utf8Decoder = new TextDecoder('utf-8');
    try {
      const response = await window.fetch(quoteFileAddress);
      const reader = response.body.getReader();
      let { value: chunk, done: readerDone } = await reader.read();
      chunk = chunk ? utf8Decoder.decode(chunk) : '';
      content = chunk;
    } catch (e) {
      alert("Unable to get quote file: " + e.message);
      return
    }
    console.log('content:', content);
    this.parseContent(content);
  }



  parseContent(content) {

  }

  run() {

  }
}

const quote = new Quotes();

quote.run();
