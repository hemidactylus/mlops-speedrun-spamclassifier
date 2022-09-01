import './App.css';

import {model_version} from '../utils/spam_utils.js';

const Header = () => {

  return (
    <header className="App-header">
      <h3 className="headerTitle"><code>SMS App</code></h3>
      <p className="headerSubtitle"><code>(using model version "{model_version}")</code></p>
    </header>
  );
}

export default Header