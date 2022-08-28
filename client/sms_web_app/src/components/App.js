import './App.css';

import Header from './Header';
import Identity from './Identity';
import SMSList from './SMSList';

import { /*useEffect,*/ useState } from "react"

const App = () => {

  const [userId, setUserId] = useState(null);

  return (
    <div className="App">
      <Header />
      <Identity
        userId={userId}
        setUserId={setUserId}
      />
      <hr />
      <SMSList
        userId={userId}
      />
    </div>
  );
}

export default App;
