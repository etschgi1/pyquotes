const quoteSeperator = /\n----\n/;
const authorSeperator = /\n\s{4}(.*?)$/;
const quoteFileAddress = 'quotes.txt';

const quoteBodyHTMLElement = 'quote-body';
const fromHTMLElement = 'from';


class Quotes {
  htmlFields = { quoteBody: null, from: null };
  quotesContainer = [];

  constructor() {
    this.htmlFields.quoteBody = document.getElementById(quoteBodyHTMLElement);
    this.htmlFields.from = document.getElementById(fromHTMLElement);
    this.getFile();
  }

   getFile() {

     fetch(quoteFileAddress)
     .then(response => {
       response.text().then(
         content => this.parseContent(content)
       )
     })
     .catch(e => alert("Unable to get quote file: " + e));

    }

  parseContent(content) {
    console.log('parseContent');
    let line = '';
    let index = 0;
    const lines = content.split(quoteSeperator);
    let len = lines.length;

    if (lines[len - 1] =~ /^(\s+)?\n+$/) {
      lines.splice(-1, 1);
      len = lines.length;
    }
    console.log(authorSeperator.test(lines[len - 1]));
    console.log(authorSeperator.match(lines[len - 1]));

  }

  getRandomQuote() {
    console.log('getRandomQuote');
  }

}

const quote = new Quotes();

quote.getRandomQuote();
