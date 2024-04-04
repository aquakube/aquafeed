import React from 'react';

import {
  Slider,
  Button,
  Grid,
  FormControl,
  FormHelperText,
  OutlinedInput,
  InputLabel,
  InputAdornment
} from '@mui/material';


export default class FeedInput extends React.Component {

    constructor(props) {
        super(props);
        this.state = {
          feedLimit: 0,
          minFeedLimit: 0,
          maxFeedLimit: 0,
          feedRate: 0,
          minFeedRate: 0,
          maxFeedRate: 0,
          timeLimit: 0,
        };

        this.handleSubmit = this.handleSubmit.bind(this);
    }

    shouldComponentUpdate(nextProps, nextState) {
      return nextProps.feedString !== this.props.feedString || nextState !== this.state;
    }

    componentDidMount() {
      const { feedString } = this.props;
      this.setState({
        feedLimit: feedString.hopper.settings.feedAmount.default,
        minFeedLimit: feedString.hopper.settings.feedAmount.min,
        maxFeedLimit: feedString.hopper.settings.feedAmount.max,
        feedRate: feedString.augers.reduce((total, auger) => total + auger.settings.feedRate.default, 0),
        minFeedRate: feedString.augers.reduce((total, auger) => total + auger.settings.feedRate.min, 0),
        maxFeedRate: feedString.augers.reduce((total, auger) => total + auger.settings.feedRate.max, 0),
        timeLimit: feedString.hopper.settings.timeLimit
      });
    }

    componentDidUpdate(prevProps, prevState) {
      const { feedString } = this.props;
      if (prevProps.feedString !== feedString) {
        this.setState({
          feedLimit: feedString.hopper.settings.feedAmount.default,
          minFeedLimit: feedString.hopper.settings.feedAmount.min,
          maxFeedLimit: feedString.hopper.settings.feedAmount.max,
          feedRate: feedString.augers.reduce((total, auger) => total + auger.settings.feedRate.default, 0),
          minFeedRate: feedString.augers.reduce((total, auger) => total + auger.settings.feedRate.min, 0),
          maxFeedRate: feedString.augers.reduce((total, auger) => total + auger.settings.feedRate.max, 0),
          timeLimit: feedString.hopper.settings.timeLimit
        });
      }
    }

    handleSubmit = (event) => {
      const { feedString, handler } = this.props;
      const { feedLimit, feedRate, timeLimit } = this.state;
      event.preventDefault();
      handler(
        {
          "feed_limit": feedLimit,
          "feed_rate": feedRate,
          "time_limit": timeLimit,
          "feed_string": feedString.name,
          "plc_readings": []
        }
      );
    };

    render() {
      const { feedLimit, feedRate, minFeedLimit, maxFeedLimit, minFeedRate, maxFeedRate } = this.state;

      return <Grid item xs={12} sm={12} md={12} sx={{ display: 'flex', justifyContent: 'flex-end' }}>
        <div style={{paddingTop: 20}}></div>
        <Grid container  rowSpacing={2} columnSpacing={{ xs: 1, sm: 1, md: 2 }}>
          <Grid item xs={12} sm={6} md={6}>
            <FormControl fullWidth variant="outlined">
              <InputLabel htmlFor="outlined-adornment-feed-limit">Feed Amount</InputLabel>
              <OutlinedInput
                id="outlined-adornment-feed-limit"
                error={feedLimit < minFeedLimit || feedLimit > maxFeedLimit}
                label="Feed Limit"
                type="number"
                value={feedLimit}
                onChange={event => this.setState({feedLimit: Number(event.target.value)})}
                endAdornment={<InputAdornment position="end">kg</InputAdornment>}
                inputProps={{
                  min: minFeedLimit,
                  max: maxFeedLimit,
                }}
              />
              <FormHelperText id="outlined-adornment-feed-limit"  error hidden={feedLimit >= minFeedLimit && feedLimit <= maxFeedLimit}>
                Must between { minFeedLimit }kg and {maxFeedRate}kg
              </FormHelperText>
            </FormControl>
          </Grid>

          <Grid item xs={12} sm={6} md={6}>
            <FormControl fullWidth variant="outlined">
              <InputLabel htmlFor="outlined-adornment-feed-rate">Feed Rate</InputLabel>
              <OutlinedInput
                id="outlined-adornment-feed-rate"
                error={feedRate < minFeedRate || feedRate > maxFeedRate}
                label="Feed Rate"
                type="number"
                value={feedRate}
                onChange={event => this.setState({feedRate: Number(event.target.value)})}
                endAdornment={<InputAdornment position="end">kg/min</InputAdornment>}
                inputProps={{
                  min: minFeedRate,
                  max: maxFeedRate,
                }}
              />
              <FormHelperText id="outlined-adornment-feed-rate" error hidden={feedRate >= minFeedRate && feedRate <= maxFeedRate}>
                Feed Rate must be between { minFeedRate} KG/M and { maxFeedRate } KG/M
              </FormHelperText>
            </FormControl>
          </Grid>

          <Grid item xs={12} sm={6} md={6}>
            <Slider
              size="small"
              min={minFeedLimit}
              max={maxFeedLimit}
              aria-label="Feed Limit"
              value={feedLimit}
              onChange={ (event, value) => this.setState({feedLimit: Number(value) })}
              // valueLabelDisplay="on"
              // marks={[
              //   {value: minFeedLimit, label: minFeedLimit},
              //   {value: maxFeedLimit, label: maxFeedLimit}
              // ]}
            />
          </Grid>
          
          <Grid item xs={12} sm={6} md={6}>
            <Slider
              size="small"
              min={minFeedRate}
              max={maxFeedRate}
              aria-label="Feed Rate"
              value={feedRate}
              onChange={ (event, value) => this.setState({feedRate: Number(value) })}
              // valueLabelDisplay="on"
              // marks={[
              //   {value: minFeedRate, label: minFeedRate},
              //   {value: maxFeedRate, label: maxFeedRate}
              // ]}
            />
          </Grid>
          
          <Grid item xs={12} sm={12} md={12} sx={{ display: 'flex', justifyContent: 'flex-end', paddingTop: '0px !important' }}>
            <Button
              fullWidth
              onClick={this.handleSubmit}
              disabled={feedRate < minFeedRate || feedRate > maxFeedRate || feedLimit < minFeedLimit || feedLimit > maxFeedLimit}
              variant="outlined"
              color="primary"
              type="submit">
              Start Feed
            </Button>
          </Grid>
        </Grid>
      </Grid>;
    }

}