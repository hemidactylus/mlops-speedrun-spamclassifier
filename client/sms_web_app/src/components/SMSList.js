import { useEffect, useState } from "react"

import './App.css';

import SMS from './SMS.js';

import {getMessages} from '../utils/sms_utils.js';

const SMSList = (props) => {

  const userId = props.userId;

  const [messageList, setMessageList] = useState([]);
  const [fetching, setFetching] = useState(false);

  const receiveMessages = (msgList) => {
    setMessageList(msgList);
    setFetching(false);
  }

  useEffect(
    () => {
      if (userId){
        setFetching(true);
        getMessages(userId, receiveMessages);
      }
    },
    [userId]
  );

  return (
    <div className="App-smslist">
    { !userId && <div>
      <p><code>(log in first.)</code></p>
    </div>}
    { userId && <div>
      {fetching && <div>
        <p><code>Fetching ...</code></p>
      </div>}
      {!fetching && <div>
        <p><code>Your inbox:</code></p>
        <code>
          <ul>
            { messageList.map( msg => (
              <li key={msg.sms_id}>
                <SMS
                  sms={msg}
                />
              </li>
            ))
            }
          </ul>
        </code>
      </div>}
    </div>}
    </div>
  );
}

export default SMSList;
