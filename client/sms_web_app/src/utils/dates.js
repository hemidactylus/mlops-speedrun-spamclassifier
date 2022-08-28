import moment from 'moment';

export const formatDate = (date0) => {
  return moment(date0).format('MMM Do, HH:mm')
}
