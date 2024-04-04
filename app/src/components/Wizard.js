import React from 'react';

import {
  Card,
  CardContent,
  Grid,
  Select,
  MenuItem
} from '@mui/material';


import FeedInput from './FeedInput.js';
import FeedStringMeta from './FeedStringMeta.js';

export default class Wizard extends React.PureComponent {

    constructor(props) {
        super(props);
        this.state = {
          selectedFeedString: this.props.feedStrings[0],
        };
    }

    render() {
      const { handler, feedStrings } = this.props;
      const { selectedFeedString } = this.state;
    
      return (
        <Card>
          <CardContent>
            <Grid container rowSpacing={2}>
              <Grid item xs={12} sm={12} md={12} sx={{ display: 'flex', justifyContent: 'flex-end' }}>
                <Select
                  fullWidth
                  value={selectedFeedString}
                  onChange={(event) => this.setState({ selectedFeedString: event.target.value })}
                  displayEmpty
                  >
                  {feedStrings.map((feedString, index) => (
                    <MenuItem key={index} value={feedString}>
                      {feedString.title}
                    </MenuItem>
                  ))}
                  </Select>
              </Grid>
              <FeedStringMeta feedString={selectedFeedString}></FeedStringMeta>
              <FeedInput feedString={selectedFeedString} handler={handler}></FeedInput>
            </Grid>
          </CardContent>
        </Card>
      );
    }

}