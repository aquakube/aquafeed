import React from 'react';
import ReactDOM from 'react-dom/client';
import ReactModal from 'react-modal';

import App from './App';

import 'react-toastify/dist/ReactToastify.css';
import './index.css';

import { BrowserRouter} from 'react-router-dom';


ReactModal.setAppElement('#root');

window.MonacoEnvironment = {
  getWorker(moduleId, label) {
    switch (label) {
      case 'css':
      case 'less':
      case 'scss':
        return new Worker(new URL('monaco-editor/esm/vs/language/css/css.worker', import.meta.url));
      case 'editorWorkerService':
        return new Worker(new URL('monaco-editor/esm/vs/editor/editor.worker', import.meta.url));
      case 'handlebars':
      case 'html':
      case 'razor':
        return new Worker(new URL('monaco-editor/esm/vs/language/html/html.worker', import.meta.url));
      case 'json':
        return new Worker(new URL('monaco-editor/esm/vs/language/json/json.worker', import.meta.url));
      case 'javascript':
      case 'typescript':
        return new Worker(new URL('monaco-editor/esm/vs/language/typescript/ts.worker', import.meta.url));
      // case 'yaml':
      //   return new Worker(new URL('monaco-yaml/lib/esm/yaml.worker', import.meta.url));
      default:
        throw new Error(`Unknown label ${label}`);
    }
  },
};

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <BrowserRouter>
    <App />
  </BrowserRouter>

  // <React.StrictMode>
  //   <App />
  // </React.StrictMode>
);
