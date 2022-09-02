import { useEffect, useState } from "react"

import './App.css';

import SMS from './SMS.js';
import RefreshList from './RefreshList.js';

import {getMessages} from '../utils/sms_utils.js';

const SMSList = (props) => {

  const userId = props.userId;

  const [messageList, setMessageList] = useState([]);
  const [fetching, setFetching] = useState(false);

  const receiveMessages = (msgList) => {
    setMessageList(msgList);
    setFetching(false);
  }

  const loadMessages = () => {
      if (userId){
        setFetching(true);
        getMessages(userId, receiveMessages);
      }
    };

  useEffect(
    loadMessages,
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
          <p>
            <RefreshList reloader={loadMessages}/>
            Your inbox:
          </p>
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
          <p>
            <RefreshList reloader={loadMessages}/>
            Your inbox is empty :|
          </p>
        </div>}
      </div>}
    </div>}
    </div>
  );
}

export default SMSList;
