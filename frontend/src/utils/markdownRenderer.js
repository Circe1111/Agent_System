import { marked } from "marked";
import hljs from "highlight.js";
import "highlight.js/styles/github.css";

// 配置marked
marked.setOptions({
  highlight: function (code, lang) {
    const language = hljs.getLanguage(lang) ? lang : "plaintext";
    return hljs.highlight(code, { language }).value;
  },
  breaks: true,
  gfm: true,
});

// 自定义渲染器
const renderer = {
  heading(text, level) {
    const sizeMap = {
      1: "2.5rem",
      2: "2rem",
      3: "1.75rem",
      4: "1.5rem",
      5: "1.25rem",
      6: "1rem",
    };
    return `<h${level} style="font-size: ${sizeMap[level]}; margin: 1.5rem 0 1rem; color: #1a365d;">${text}</h${level}>`;
  },
  paragraph(text) {
    return `<p style="line-height: 1.6; margin: 1rem 0; color: #4a5568;">${text}</p>`;
  },
  link(href, title, text) {
    return `<a href="${href}" title="${title || ""}" target="_blank" style="color: #3182ce; text-decoration: none; font-weight: 500;">${text}</a>`;
  },
  image(href, title, text) {
    return `<img src="${href}" alt="${text}" title="${title || ""}" style="max-width: 100%; border-radius: 8px; margin: 1rem 0;" />`;
  },
  code(code, lang) {
    return `<pre><code class="hljs ${lang || ""}" style="background: #f7fafc; padding: 1rem; border-radius: 8px; overflow-x: auto;">${code}</code></pre>`;
  },
};

Object.assign(marked.getRenderer(), renderer);

export const renderMarkdown = (content) => {
  if (!content) return "";
  return marked.parse(content);
};

export const streamMarkdown = (content, callback, speed = 50) => {
  let index = 0;
  const timer = setInterval(() => {
    if (index < content.length) {
      callback(content.substring(0, index + 1));
      index++;
    } else {
      clearInterval(timer);
    }
  }, speed);
  return timer;
};

export default {
  renderMarkdown,
  streamMarkdown,
};
