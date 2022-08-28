import axios from "axios";

export const getMessages = (userId, callback) => {
  axios.get(`http://localhost:8111/sms/${userId}`)
    .then(response => {
      callback(response.data);
    }
  );
}
