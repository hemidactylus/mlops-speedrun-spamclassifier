import { /*useEffect,*/ useState } from "react"

import './App.css';


const Identity = (props) => {

  const userId = props.userId;
  const setUserId = props.setUserId;

  const [editUserId, setEditUserId] = useState('');


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
          />
          <button
            onClick={() => {
              if(setUserId){
                setUserId(editUserId);
              }
            }}
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
