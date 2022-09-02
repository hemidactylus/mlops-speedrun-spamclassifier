import './App.css';

import { /*useEffect,*/ useState } from "react"

import {formatDate} from '../utils/dates.js';
import {checkSpamStatus} from '../utils/spam_utils.js';

const SMS = ({sms}) => {

  const [spamStatus, setSpamStatus] = useState('U');

  const receiveSpamStatus = (pred_top) => {
    if (pred_top === 'ham'){
      setSpamStatus('H');
    } else {
      setSpamStatus('S');
    }
  };

  const renderSpamStatus = (s) => {
    if (s === 'U'){
      return '🔍';
    } else if (s === 'W'){
      return '⏳';
    } else if (s === 'H'){
      return '✅';
    } else if (s === 'S'){
      return '❌';
    } else {
      return '?';
    }
  }

  return (
    <div>
      <span className="spamStatus">
        { (spamStatus === 'U') &&
          <span
            onClick={ () => {
              setSpamStatus('W');
              checkSpamStatus(sms.sms_text, sms.sms_id, receiveSpamStatus);
            }}
          >{renderSpamStatus(spamStatus)}</span>
        }
        { (spamStatus !== 'U') &&
          <span>{renderSpamStatus(spamStatus)}</span>
        }
      </span>
      [
        <span className="smsDate">{formatDate(sms.date_sent)}</span>,
        <span className="smsSender">{sms.sender_id}</span>
      ]
      <span className="smsText">{sms.sms_text}</span>
    </div>
  );
}

export default SMS
