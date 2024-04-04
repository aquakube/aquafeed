import React from 'react';

import {
  Tab,
  Tabs,
  Box
} from '@mui/material';

import Editor from '@monaco-editor/react';


function sortKeys(obj) {
  let sortedObj = {};
  let keys = Object.keys(obj);
  keys.sort((a, b) => {
    if (typeof obj[a] === 'object' && typeof obj[b] === 'object') {
      return a.localeCompare(b);
    } else if (typeof obj[a] !== 'object' && typeof obj[b] !== 'object') {
      return a.localeCompare(b);
    } else if (typeof obj[a] === 'object') {
      return 1;
    } else {
      return -1;
    }
  });

  for (let key of keys) {
    if (typeof obj[key] === 'object') {
      sortedObj[key] = sortKeys(obj[key]);
    } else {
      sortedObj[key] = obj[key];
    }
  }

  return sortedObj;
}

export default class FeedString extends React.Component {

    constructor(props) {
        super(props);
        this.state = {
          selectedTab: 0,
        };
    }

    handleTabChange = (event, newValue) => {
      this.setState({ selectedTab: newValue });
    };
  
    render() {
      const { feedStrings } = this.props;

      return (
        <>
          <Tabs value={this.state.selectedTab} onChange={this.handleTabChange}>
            {feedStrings.map((feedString, index) => (
              <Tab label={feedString.title} key={index} />
            ))}
          </Tabs>
          {this.state.selectedTab !== -1 && (
            <Box sx={{ height: window.innerHeight - 150 }}>
              <Editor
                value={JSON.stringify(sortKeys(feedStrings[this.state.selectedTab]), null, 2)}
                options={{ automaticLayout: true }}
              />
            </Box>
          )}
        </>
      );
    }

}