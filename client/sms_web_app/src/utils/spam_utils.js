import axios from "axios";

export const model_version = process.env.REACT_APP_SPAM_MODEL_VERSION || 'v1';
export const architecture_version = process.env.REACT_APP_ARCHITECTURE_VERSION || 'I';

export const checkSpamStatus = (sms_text, sms_id, callback, error_callback) => {
  if (architecture_version === 'I') {
    axios.post(
      `http://localhost:8000/model/${model_version}/text_to_prediction`,
      {
        text: sms_text
      }
    )
      .then(response => {
        callback(response.data.top.label);
      }
    )
      .catch(error => {
        if(error_callback){
          error_callback();
        }
      }
    );
  } else if (architecture_version === 'II') {
    axios.post(
      'http://127.0.0.1:8999/get-online-features',
      {
        feature_service: 'labeled_sms_2',
        entities: {
          sms_id: [sms_id]
        }
      }
    )
      .then(response => {
        const features_index = response.data.metadata.feature_names.indexOf('features');
        const features = response.data.results[features_index].values[0];
        // now to the model-serving API
        axios.post(
          `http://localhost:8000/model/${model_version}/features_to_prediction`,
          {
            features: features
          }
        )
          .then(response => {
            callback(response.data.top.label);
          }
        )
          .catch(error => {
            if(error_callback){
              error_callback();
            }
          }
        );
      }
    );
  }
}
