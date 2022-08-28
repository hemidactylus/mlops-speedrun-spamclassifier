import axios from "axios";

const model_version = process.env.REACT_APP_SPAM_MODEL_VERSION || 'v1';

export const checkSpamStatus = (sms_text, callback) => {
  axios.post(
    `http://localhost:8000/model/${model_version}/text_to_prediction`,
    {
      text: sms_text
    }
  )
    .then(response => {
      callback(response.data.top.label);
    }
  );
}
