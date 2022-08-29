import { /*useEffect,*/ useState } from "react"

import './App.css';


const Identity = (props) => {

  const userId = props.userId;
  const setUserId = props.setUserId;

  const [editUserId, setEditUserId] = useState('');

  const trySetUserId = (newUserId) => {
    if(newUserId){
      setUserId(newUserId);
    }
  }

  return (
    <div className="App-identity">
      { !userId && <div>
        <p>
          <code>Who are you?</code>
          <input
            className="inlineInput"
            type="text"
            name="userid"
            value={editUserId}
            onChange={(e) => setEditUserId(e.target.value)}
            onKeyPress={(e) => {if (e.key === 'Enter') { trySetUserId(editUserId) }}}
          />
          <button
            onClick={() => trySetUserId(editUserId)}
            className="inlineButton"
          >
            Login
          </button>
        </p>
      </div>}
      { userId && <div>
        <p>
          <code>Welcome, {userId}</code>

          <button
            onClick={() => {
              setUserId(null);
            }}
            className="inlineButton"
          >
            Logout
          </button>

        </p>

      </div>}
    </div>
  );
}

export default Identity
