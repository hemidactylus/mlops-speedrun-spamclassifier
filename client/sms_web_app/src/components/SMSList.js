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
      <p>(log in first.)</p>
    </div>}
    { userId && <div>
      {fetching && <div>
        <p>Fetching ...</p>
      </div>}
      {!fetching && <div>
        { (messageList.length > 0) && <div>
          <p>Your inbox:</p>
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
        </div>}
        { (messageList.length === 0) && <div>
          <p>Your inbox is empty :|</p>
        </div>}        
      </div>}
    </div>}
    </div>
  );
}

export default SMSList;
