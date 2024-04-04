import React from 'react';
import Editor from '@monaco-editor/react';
import CloseIcon from '@mui/icons-material/Close';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  IconButton
} from '@mui/material';

export default class EventDialog extends React.PureComponent {

  constructor(props) {
    super(props);

    this.state = {};
  }

  componentDidMount() {

  }

  render() {
    const { open, event, onClose } = this.props;

    return (
      <div className='event_dialog'>
        <Dialog fullWidth maxWidth='md' open={open} onClose={onClose} >
          <DialogTitle sx={{ m: 0, p: 2 }}>
            Event
          </DialogTitle>
          <IconButton
            onClick={onClose}
            sx={{
              position: 'absolute',
              right: 8,
              top: 8,
              color: (theme) => theme.palette.grey[500],
            }}
          >
            <CloseIcon />
          </IconButton>
          <DialogContent style={{
            height: '50vh',
            maxHeight: '500px',
          }}>
            <Editor
              height="100%"
              width="100%"
              defaultLanguage="json"
              value={JSON.stringify(event?.data, null, 2)}
              theme="vs-dark"
              options={{
                scrollBeyondLastLine: false,
                lineNumbers: "on",
                fontSize: "14px",
                wordWrap: "on",
                readOnly: true,
                minimap: {
                  enabled: false
                }
              }}
            />
          </DialogContent>

        </Dialog>
      </div>
    );
  }
}