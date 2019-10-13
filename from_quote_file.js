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
    lines.forEach(item => {
      const quote = {
        text: '',
      }

      if (authorSeperator.test(item)) {
        quote.author = item.match(authorSeperator)[1].replace(/\n/, ' ');
        quote.text = item.replace(authorSeperator, '').replace(/\n/, ' ');
      } else {
        quote.text = item.replace(/\n/, ' ');
      }

      this.quotesContainer.push(quote);
    });

    this.getRandomQuote();
  }

  getRandomInt(max) {
    return Math.floor(Math.random() * Math.floor(max));
  }

  getRandomQuote() {
    const rand = this.getRandomInt(this.quotesContainer.length);

    const quote = this.quotesContainer[rand];
    this.htmlFields.quoteBody.innerText = quote.text;
    if (quote.author) {
      this.htmlFields.from.innerText = '—' + quote.author
    } else {
      this.htmlFields.from.innerText = '';
    }
  }

}

const quote = new Quotes();

