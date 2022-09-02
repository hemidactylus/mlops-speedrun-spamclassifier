import './App.css';

const RefreshList = (props) => {

  const reloader = props.reloader;

  return (
    <span
      className="reloadButton"
      onClick={reloader}
    >🔄</span>
  );
}

export default RefreshList;
