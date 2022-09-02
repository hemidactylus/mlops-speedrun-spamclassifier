import './App.css';

import {model_version, architecture_version} from '../utils/spam_utils.js';

const Header = () => {

  return (
    <header className="App-header">
      <h3 className="headerTitle">SMS App</h3>
      <p className="headerSubtitle">(using model version "{model_version}"; architecture version "{architecture_version}")</p>
    </header>
  );
}

export default Header
