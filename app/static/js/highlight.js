
const highlightText = (text, spans) => {
  var innerText = ''
  var lastEnd = 0;

  spans.forEach(s => {
    const start = s[0];
    const end = s[1];
    const beforeText = text.slice(lastEnd, start);
    const highlighted = text.slice(start, end);
    innerText += `${beforeText}<span class="highlight">${highlighted}</span>`;
    lastEnd = end;
  });

  if (lastEnd < text.length) {
    innerText += text.slice(lastEnd, text.length);
  }
  
  return innerText;
}