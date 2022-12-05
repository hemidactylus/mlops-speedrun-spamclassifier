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

  const receiveErrorFromSpamService = () => {
    setSpamStatus('E');
  }

  const renderSpamStatus = (s) => {
    if (s === 'U'){
      // unknown yet
      return '🔍';
    } else if (s === 'W'){
      // waiting for response
      return '⏳';
    } else if (s === 'H'){
      // not spam
      return '✅';
    } else if (s === 'S'){
      // spam
      return '🗑️';
    } else if (s === 'E'){
      // error from API
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
              checkSpamStatus(sms.sms_text, sms.sms_id, receiveSpamStatus, receiveErrorFromSpamService);
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
